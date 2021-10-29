"""Global NDR Processing Pipeline."""
import argparse
import collections
import glob
import logging
import importlib
import multiprocessing
import os
import pathlib
import re
import subprocess
import sqlite3
import shutil
import time
import threading
import zipfile

from inspring.ndr_plus.ndr_plus import ndr_plus
from osgeo import gdal
from osgeo import osr
import ecoshard
import pandas
import pygeoprocessing
import numpy
import retrying
import taskgraph

gdal.SetCacheMax(2**27)
logging.getLogger('taskgraph').setLevel(logging.INFO)

# Using an ENV-defined workspace means we can run multiple individual scenarios
# in different workspaces separately.
try:
    WORKSPACE_DIR = os.environ['WORKSPACE_DIR']
except KeyError:
    WORKSPACE_DIR = 'global_ndr_plus_workspace'

ECOSHARD_DIR = os.path.join(WORKSPACE_DIR, 'ecoshards')
SCRUB_DIR = os.path.join(ECOSHARD_DIR, 'scrubbed_ecoshards')
WORK_STATUS_DATABASE_PATH = os.path.join(WORKSPACE_DIR, 'work_status.db')
SCHEDULED_STATUS = 'scheduled'  # use when scheduled but no work done
COMPUTED_STATUS = 'computed'  # use when computed but not stitched
COMPLETE_STATUS = 'complete'  # use when stitched and deleted
USE_AG_LOAD_ID = 999

# All links in this dict is an ecoshard that will be downloaded to
# ECOSHARD_DIR
ECOSHARD_PREFIX = 'https://storage.googleapis.com/'

WATERSHED_ID = 'hydrosheds_15arcseconds'

# Known properties of the DEM:
DEM_ID = 'global_dem_3s'
DEM_TILE_DIR = os.path.join(ECOSHARD_DIR, 'global_dem_3s')
DEM_VRT_PATH = os.path.join(DEM_TILE_DIR, 'global_dem_3s.vrt')

# Global properties of the simulation
RETENTION_LENGTH_M = 150
K_VAL = 1.0
TARGET_CELL_LENGTH_M = 300
FLOW_THRESHOLD = int(500**2*90 / TARGET_CELL_LENGTH_M**2)
MAX_PIXEL_FILL_COUNT = 500  # distance to search to fill a pixel
ROUTING_ALGORITHM = 'D8'
TARGET_WGS84_LENGTH_DEG = 10/3600
BASE_WGS84_LENGTH_DEG = 10/3600/2
AREA_DEG_THRESHOLD = 0.000016 * 10  # this is 10 times larger than hydrosheds 1 "pixel" watersheds

# base ecoshards that will be added to by scenario modules
ECOSHARDS = {
    DEM_ID: f'{ECOSHARD_PREFIX}ipbes-ndr-ecoshard-data/global_dem_3s_blake2b_0532bf0a1bedbe5a98d1dc449a33ef0c.zip',
    WATERSHED_ID: f'{ECOSHARD_PREFIX}ipbes-ndr-ecoshard-data/watersheds_globe_HydroSHEDS_15arcseconds_blake2b_14ac9c77d2076d51b0258fd94d9378d4.zip',
}
# these are defined from scenario modules
BIOPHYSICAL_TABLE_IDS = {}
SCENARIOS = {}
SCRUB_IDS = set()


def _setup_logger(name, log_filename, level):
    """Create arbitrary logger to file.

    Args:
        name (str): arbitrary name of logger
        log_filename (str): filename in workspace to log to
        level (logging.LEVEL): the log level to report.

    Return:
        logger object
    """
    handler = logging.FileHandler(os.path.join(WORKSPACE_DIR, log_filename))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


LOGGER = _setup_logger('cbd_global_ndr_plus', 'log.out', level=logging.DEBUG)
PYGEOPROCESSING_LOGGER = _setup_logger('pygeoprocessing', 'pygeoprocessinglog.out', level=logging.INFO)
INSPRING_LOGGER = _setup_logger('inspring', 'inspringlog.out', level=logging.DEBUG)
REPORT_WATERSHED_LOGGER = _setup_logger('report_watershed', 'report_watershed.out', level=logging.DEBUG)
ECOSHARD_LOGGER = _setup_logger('ecoshard', 'ecoshard.out', level=logging.DEBUG)


@retrying.retry(
    wait_exponential_multiplier=500, wait_exponential_max=3200,
    stop_max_attempt_number=100)
def _execute_sqlite(
        sqlite_command, database_path, argument_list=None,
        mode='read_only', execute='execute', fetch=None):
    """Execute SQLite command and attempt retries on a failure.

    Args:
        sqlite_command (str): a well formatted SQLite command.
        database_path (str): path to the SQLite database to operate on.
        argument_list (list): ``execute == 'execute'`` then this list is passed
            to the internal sqlite3 ``execute`` call.
        mode (str): must be either 'read_only' or 'modify'.
        execute (str): must be either 'execute', 'executemany,' or 'script'.
        fetch (str): if not ``None`` can be either 'all' or 'one'.
            If not None the result of a fetch will be returned by this
            function.

    Returns:
        result of fetch if ``fetch`` is not None.

    """
    cursor = None
    connection = None
    try:
        if mode == 'read_only':
            ro_uri = r'%s?mode=ro' % pathlib.Path(
                os.path.abspath(database_path)).as_uri()
            connection = sqlite3.connect(ro_uri, uri=True)
        elif mode == 'modify':
            connection = sqlite3.connect(database_path)
        else:
            raise ValueError('Unknown mode: %s' % mode)

        if execute == 'execute':
            if argument_list is None:
                cursor = connection.execute(sqlite_command)
            else:
                cursor = connection.execute(sqlite_command, argument_list)
        elif execute == 'script':
            cursor = connection.executescript(sqlite_command)
        elif execute == 'executemany':
            cursor = connection.executemany(sqlite_command, argument_list)
        else:
            raise ValueError('Unknown execute mode: %s' % execute)

        result = None
        payload = None
        if fetch == 'all':
            payload = (cursor.fetchall())
        elif fetch == 'one':
            payload = (cursor.fetchone())
        elif fetch is not None:
            raise ValueError('Unknown fetch mode: %s' % fetch)
        if payload is not None:
            result = list(payload)
        cursor.close()
        connection.commit()
        connection.close()
        cursor = None
        connection = None
        return result
    except sqlite3.OperationalError:
        LOGGER.exception(
            f'{database_path} database is locked because another process is '
            'using it, waiting for a bit of time to try again\n'
            f'{sqlite_command}')
        raise
    except Exception:
        LOGGER.exception(
            f'Exception on _execute_sqlite: {sqlite_command}\n'
            f'  and the argument list is: {argument_list}')
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.commit()
            connection.close()


def _create_work_table_schema(database_path):
    """Create database exists and/or ensures it is compatible and recreate.

    Args:
        database_path (str): path to an existing database or desired
            location of a new database.

    Returns:
        None.

    """
    sql_create_table_script = (
        """
        CREATE TABLE work_status (
            scenario_id TEXT NOT NULL,
            watershed_id TEXT NOT NULL,
            watershed_area FLOAT NOT NULL,
            status TEXT NOT NULL,
            PRIMARY KEY (scenario_id, watershed_id)
        );
        """)

    # create the base table
    _execute_sqlite(
        sql_create_table_script, database_path,
        mode='modify', execute='script')


def _set_work_status(database_path, watershed_id_status_list):
    try:
        sql_statement = '''
            UPDATE work_status
            SET status=?
            WHERE scenario_id=? AND watershed_id=?;
        '''
        _execute_sqlite(
            sql_statement, database_path,
            argument_list=watershed_id_status_list,
            mode='modify', execute='executemany')
    except Exception as e:
        LOGGER.exception(f'{e} happened on work status with status list of {watershed_id_status_list}')
        raise


def detect_invalid_values(base_raster_path, rtol=0.001, max_abs=1e30):
    """Return error if an invalid value is found in the raster.

    A return value of errors are raised if there are any non-finite values, any
    values that are close to nodata but not equal to nodata, or any values that
    are just really big. If none of these are true then the function returns
    ``True``.
    """
    numpy.set_printoptions(precision=15)
    base_nodata = pygeoprocessing.get_raster_info(
        base_raster_path)['nodata'][0]
    for _, block_array in pygeoprocessing.iterblocks((base_raster_path, 1)):
        non_finite_mask = ~numpy.isfinite(block_array)
        if non_finite_mask.any():
            return (
                f'found some non-finite values in {base_raster_path}: '
                f'{block_array[non_finite_mask]}')
        if base_nodata is not None:
            close_to_nodata_mask = numpy.isclose(
                block_array, base_nodata, rtol=rtol) & ~numpy.isclose(
                block_array, base_nodata)
            if close_to_nodata_mask.any():
                return (
                    f'found some values that are close to nodata {base_nodata} '
                    f'but not equal to '
                    f'nodata in {base_raster_path}: '
                    f'{block_array[close_to_nodata_mask]}')

        large_value_mask = (numpy.abs(block_array) >= max_abs)
        if base_nodata is not None:
            large_value_mask &= ~numpy.isclose(block_array, base_nodata)
        if large_value_mask.any():
            return (
                f'found some very large values not close to {base_nodata} in '
                f'{base_raster_path}: {block_array[large_value_mask]}')

    return True


def scrub_raster(
        base_raster_path, target_raster_path, target_nodata=None,
        rtol=0.001, max_abs=1e30):
    """Scrub invalid values from base.

    Will search base raster for difficult values like NaN, +-inf, Very Large
    values that may indicate a roundoff error when being compared to nodata.

    Args:
        base_raster_path (str): path to base raster
        target_raster_path (str): path to raster created by this call with
            invalid values 'scrubbed'.
        target_nodata (numeric): if `None` then the nodata value is copied
            from base, otherwise it is set to this value.
        rtol (float): relative tolerance to use when comparing values with
            nodata. Default is set to 1-3.4e38/float32.min.
        max_abs (float): the maximum absolute value to expect in the raster
            anything larger than this will be set to nodata. Defaults to
            1e30.

    Return:
        None
    """
    LOGGER.debug(f'scrubbing {base_raster_path}')
    if (os.path.exists(target_raster_path) and
            os.path.samefile(base_raster_path, target_raster_path)):
        raise ValueError(
            f'{base_raster_path} and {target_raster_path} are the same file')
    base_raster_info = pygeoprocessing.get_raster_info(base_raster_path)
    base_nodata = base_raster_info['nodata'][0]
    if base_nodata is None and target_nodata is None:
        raise ValueError('value base and target nodata are both None')
    if (base_nodata is not None and
            target_nodata is not None and
            base_nodata != target_nodata):
        raise ValueError(
            f'base raster at {base_raster_path} has a defined nodata '
            f'value of {base_nodata} and also a requested '
            f'target {target_nodata} value')
    if target_nodata is None:
        scrub_nodata = base_nodata
    else:
        scrub_nodata = target_nodata

    non_finite_count = 0
    large_value_count = 0
    close_to_nodata = 0

    def _scrub_op(base_array):
        nonlocal non_finite_count
        nonlocal large_value_count
        nonlocal close_to_nodata
        result = numpy.copy(base_array)
        non_finite_mask = ~numpy.isfinite(result)
        non_finite_count += numpy.count_nonzero(non_finite_mask)
        result[non_finite_mask] = scrub_nodata

        large_value_mask = numpy.abs(result) >= max_abs
        large_value_count += numpy.count_nonzero(large_value_mask)
        result[large_value_mask] = scrub_nodata

        close_to_nodata_mask = numpy.isclose(
            result, scrub_nodata, rtol=rtol)
        close_to_nodata += numpy.count_nonzero(close_to_nodata_mask)
        result[close_to_nodata_mask] = scrub_nodata
        return result

    LOGGER.debug(
        f'starting raster_calculator op for scrubbing {base_raster_path}')
    pygeoprocessing.raster_calculator(
        [(base_raster_path, 1)], _scrub_op, target_raster_path,
        base_raster_info['datatype'], scrub_nodata)

    if any([non_finite_count, large_value_count, close_to_nodata]):
        LOGGER.warning(
            f'{base_raster_path} scrubbed these values:\n'
            f'\n\tnon_finite_count: {non_finite_count}'
            f'\n\tlarge_value_count: {large_value_count}'
            f'\n\tclose_to_nodata: {close_to_nodata} '
            f'\n\tto the nodata value of: {scrub_nodata}')
    else:
        LOGGER.info(f'{base_raster_path} is CLEAN')


def create_empty_wgs84_raster(cell_size, nodata, target_path):
    """Create an empty wgs84 raster to cover all the world."""
    n_cols = int(360 // cell_size)
    n_rows = int(180 // cell_size)
    gtiff_driver = gdal.GetDriverByName('GTIFF')
    target_raster = gtiff_driver.Create(
        target_path, n_cols, n_rows, 1, gdal.GDT_Float32,
        options=(
            'TILED=YES', 'BIGTIFF=YES', 'COMPRESS=LZW',
            'BLOCKXSIZE=256', 'BLOCKYSIZE=256'))

    target_band = target_raster.GetRasterBand(1)
    target_band.SetNoDataValue(nodata)
    wgs84_srs = osr.SpatialReference()
    wgs84_srs.ImportFromEPSG(4326)
    target_raster.SetProjection(wgs84_srs.ExportToWkt())
    target_raster.SetGeoTransform(
        [-180, cell_size, 0.0, 90.0, 0.0, -cell_size])
    target_raster = None


@retrying.retry(stop_max_attempt_number=100)
def stitch_worker(
        scenario_id, stitch_export_raster_path,
        stitch_modified_load_raster_path,
        stitch_queue, remove_workspaces):
    """Take elements from stitch queue and stitch into target."""
    try:
        export_raster_list = []
        modified_load_raster_list = []
        workspace_list = []
        status_update_list = []
        watershed_process_count = collections.defaultdict(int)
        while True:
            payload = stitch_queue.get()
            if payload is not None:
                (export_raster_path, modified_load_raster_path,
                 workspace_dir, watershed_basename, watershed_id) = payload
                watershed_process_count[watershed_basename] += 1
                status_update_list.append(
                    (COMPLETE_STATUS, scenario_id, watershed_id))

                export_raster_list.append((export_raster_path, 1))
                modified_load_raster_list.append((modified_load_raster_path, 1))
                workspace_list.append(workspace_dir)

                for path in (export_raster_path, modified_load_raster_path):
                    if not os.path.exists(path):
                        raise ValueError(
                            f'this path {path} was to stitch into '
                            f'{stitch_export_raster_path} or '
                            f'{stitch_modified_load_raster_path} but does not '
                            'exist: ')

            if len(workspace_list) < 100 and payload is not None:
                continue

            worker_list = []
            for target_stitch_raster_path, raster_list in [
                    (stitch_export_raster_path, export_raster_list),
                    (stitch_modified_load_raster_path,
                     modified_load_raster_list)]:
                stitch_worker = threading.Thread(
                    target=pygeoprocessing.stitch_rasters,
                    args=(
                        raster_list,
                        ['near']*len(raster_list),
                        (target_stitch_raster_path, 1)),
                    kwargs={
                        'overlap_algorithm': 'etch',
                        'area_weight_m2_to_wgs84': True})
                stitch_worker.start()
                worker_list.append((stitch_worker, raster_list))
            for worker, raster_list in worker_list:
                LOGGER.debug(f'waiting for this raster list to stitch: {raster_list}')
                worker.join()
                LOGGER.debug(f'done on that last stitch')
            if remove_workspaces:
                LOGGER.debug(f'removing {len(workspace_list)} workspaces')
                for workspace_dir in workspace_list:
                    shutil.rmtree(workspace_dir)

            export_raster_list = []
            modified_load_raster_list = []
            workspace_list = []
            watershed_process_count = collections.defaultdict(int)

            _set_work_status(
                WORK_STATUS_DATABASE_PATH,
                status_update_list)
            status_update_list = []

            if payload is None:
                stitch_queue.put(None)
                break
        if payload is None and remove_workspaces is not None:
            # all done, time to build overview and compress
            LOGGER.debug(
                f'building overviews and compressing results '
                f'for {stitch_export_raster_path} and '
                f'{stitch_modified_load_raster_path}')
            build_overview_thread_list = []
            for base_raster_path in [
                    stitch_export_raster_path,
                    stitch_modified_load_raster_path]:
                upsample_raster_path = os.path.join(
                    WORKSPACE_DIR,
                    f'upsample_{os.path.basename(base_raster_path)}')
                compressed_raster_path = os.path.join(
                    WORKSPACE_DIR,
                    f'compressed_{os.path.basename(base_raster_path)}')
                build_overview_process = threading.Thread(
                    target=upsample_compress_and_overview,
                    args=(
                        base_raster_path, upsample_raster_path,
                        compressed_raster_path))
                build_overview_process.start()
                build_overview_thread_list.append(build_overview_process)
            LOGGER.debug('joining the build overview threads')
            for process in build_overview_thread_list:
                process.join()
            LOGGER.debug(f'all done stitching for {scenario_id}')
    except Exception:
        LOGGER.exception(
            f'something bad happened on ndr stitcher for {scenario_id}')
        raise


def _create_watershed_id(watershed_path, watershed_fid):
    """Create unique ID from path and FID."""
    watershed_basename = os.path.basename(os.path.splitext(watershed_path)[0])
    return (watershed_basename, f'{watershed_basename}_{watershed_fid}')


def _split_watershed_id(watershed_id):
    """Split into watershed basename and fid."""
    basename, fid = re.match(r'^(.*)_(\d*)$', watershed_id).groups()
    return (basename, int(fid))


def ndr_plus_and_stitch(
        scenario_id,
        watershed_path, watershed_fid,
        target_cell_length_m,
        retention_length_m,
        k_val,
        flow_threshold,
        max_pixel_fill_count,
        routing_algorithm,
        dem_path,
        lulc_path,
        precip_path,
        custom_load_path,
        eff_n_lucode_map,
        load_n_lucode_map,
        target_export_raster_path,
        target_modified_load_raster_path,
        workspace_dir,
        stitch_queue):
    """Invoke ``inspring.ndr_plus`` with stitch.

    Same parameter list as ``inspring.ndr_plus`` with additional args:

    stitch_queue (queue): places export, load, and workspace path here to
        stitch globally and delete the workspace when complete.

    Return:
        ``None``
    """
    try:
        watershed_basename, watershed_id = _create_watershed_id(watershed_path, watershed_fid)
        LOGGER.debug(f'{watershed_id} about to be run')
        ndr_plus(
            watershed_path,
            watershed_fid,
            target_cell_length_m,
            retention_length_m,
            k_val,
            flow_threshold,
            max_pixel_fill_count,
            routing_algorithm,
            dem_path,
            lulc_path,
            precip_path,
            custom_load_path,
            eff_n_lucode_map,
            load_n_lucode_map,
            target_export_raster_path,
            target_modified_load_raster_path,
            workspace_dir)

        LOGGER.debug(f'{watershed_id} is done')
        _set_work_status(
            WORK_STATUS_DATABASE_PATH,
            [(COMPUTED_STATUS, scenario_id, watershed_id)])
        stitch_queue.put(
            (target_export_raster_path, target_modified_load_raster_path,
             workspace_dir, watershed_basename, watershed_id))
    except Exception as e:
        LOGGER.exception(
            f'this exception happened on {watershed_path} {watershed_fid}, '
            f'skipping and logging the error in the database.')
        _set_work_status(
            WORK_STATUS_DATABASE_PATH,
            [(f'exception happened: {e}', scenario_id, watershed_id)])


def load_biophysical_table(biophysical_table_path, lulc_field_id):
    """Dump the biophysical table to two dictionaries indexable by lulc.

    Args:
        biophysical_table_path (str): biophysical table that indexes lulc
            codes to 'eff_n' and 'load_n' values. These value can have
            the field 'use raster' in which case they will be replaced with
            a custom raster layer for the lulc code.
        lulc_field_id (str): this is the name of the field that references
            the lulc id.

    Return:
        A tuple of:
        * eff_n_lucode_map: index lulc to nitrogen efficiency
        * load_n_lucode_map: index lulc to base n load
    """
    biophysical_table = pandas.read_csv(biophysical_table_path)
    # clean up biophysical table
    biophysical_table = biophysical_table.fillna(0)
    biophysical_table.loc[
        biophysical_table['load_n'] == 'use raster', 'load_n'] = (
            USE_AG_LOAD_ID)
    biophysical_table['load_n'] = biophysical_table['load_n'].apply(
        pandas.to_numeric)

    eff_n_lucode_map = dict(
            zip(biophysical_table[lulc_field_id], biophysical_table['eff_n']))
    load_n_lucode_map = dict(
        zip(biophysical_table[lulc_field_id], biophysical_table['load_n']))
    return eff_n_lucode_map, load_n_lucode_map


def unzip(zipfile_path, target_unzip_dir):
    """Unzip zip to target_dir."""
    LOGGER.info(f'unzip {zipfile_path} to {target_unzip_dir}')
    os.makedirs(target_unzip_dir, exist_ok=True)
    with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
        zip_ref.extractall(target_unzip_dir)


def unzip_and_build_dem_vrt(
        zipfile_path, target_unzip_dir, expected_tiles_zip_path,
        target_vrt_path):
    """Build VRT of given tiles.

    Args:
        zipfile_path (str): source zip file to extract.
        target_unzip_dir (str): desired directory in which to extract
            the zipfile.
        expected_tiles_zip_path (str): the expected directory to find the
            geotiff tiles after the zipfile has been extracted to
            ``target_unzip_dir``.
        target_vrt_path (str): path to desired VRT file of those files.

    Return:
        ``None``
    """
    unzip(zipfile_path, target_unzip_dir)
    LOGGER.info('build vrt')
    subprocess.run(
        f'gdalbuildvrt {target_vrt_path} {expected_tiles_zip_path}/*.tif',
        shell=True)
    LOGGER.info(f'all done building {target_vrt_path}')


def _report_watershed_count():
    try:
        start_time = time.time()
        count_to_process_sql = '''
            SELECT count(1) FROM work_status
            WHERE status!=?'''
        original_watershed_to_process_count = _execute_sqlite(
            count_to_process_sql, WORK_STATUS_DATABASE_PATH,
            fetch='one', argument_list=[COMPLETE_STATUS])[0]
        sleep_time = 15.0
        while True:
            time.sleep(sleep_time)
            current_remaining_to_process = _execute_sqlite(
                count_to_process_sql, WORK_STATUS_DATABASE_PATH,
                argument_list=[COMPLETE_STATUS], fetch='one')[0]

            watersheds_processed_so_far = (
                original_watershed_to_process_count - current_remaining_to_process)

            seconds_so_far = time.time() - start_time
            n_processed_per_sec = watersheds_processed_so_far / seconds_so_far
            if n_processed_per_sec > 0:
                seconds_left = current_remaining_to_process / n_processed_per_sec
            else:
                seconds_left = 99999999999
            hours_left = int(seconds_left // 3600)
            seconds_left -= hours_left * 3600
            minutes_left = int(seconds_left // 60)
            seconds_left -= minutes_left * 60

            hours_so_far = int(seconds_so_far // 3600)
            seconds_so_far -= hours_so_far * 3600
            minutes_so_far = int(seconds_so_far // 60)
            seconds_so_far -= minutes_so_far * 60
            REPORT_WATERSHED_LOGGER.info(
                f'\n******\ntotal left: {current_remaining_to_process}'
                f'\ntotal completed: {original_watershed_to_process_count-current_remaining_to_process}' +
                f'\ntime left: {hours_left}:{minutes_left:02d}:{seconds_left:04.1f}' +
                f'\ntime so far: {hours_so_far}:{minutes_so_far:02d}:{seconds_so_far:04.1f}')

    except Exception:
        REPORT_WATERSHED_LOGGER.exception('something bad happened')
        raise


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description='Run CBD data pipeline')
    parser.add_argument(
        'scenario_module_name', nargs='+', help='scenario module(s) to load.')
    parser.add_argument(
        '--n_workers', type=int, default=multiprocessing.cpu_count(),
        help='number of workers for Taskgraph.')
    parser.add_argument(
        '--watersheds', type=str, nargs='+',
        help='comma separated list of watershed-basename,fid to simulate')
    parser.add_argument(
        '--limit_to_scenarios', type=str, nargs='+',
        help='list the scenario keys which this run should only do.')
    args = parser.parse_args()

    for scenario_module_name in args.scenario_module_name:
        scenario_module = importlib.import_module(scenario_module_name)
        LOGGER.debug(f'updating ECOSHARDS with {scenario_module.ECOSHARDS}')
        ECOSHARDS.update(scenario_module.ECOSHARDS)
        LOGGER.debug(f'updating BIOPHYSICAL_TABLE_IDS with {scenario_module.BIOPHYSICAL_TABLE_IDS}')
        BIOPHYSICAL_TABLE_IDS.update(scenario_module.BIOPHYSICAL_TABLE_IDS)
        LOGGER.debug(f'updating SCENARIOS with {scenario_module.SCENARIOS}')
        if args.limit_to_scenarios:
            SCENARIOS.update(
                {key: value for key, value in
                 scenario_module.SCENARIOS.items()
                 if key in args.limit_to_scenarios})
        else:
            SCENARIOS.update(scenario_module.SCENARIOS)
        LOGGER.debug(f'updating SCRUB_IDS with {scenario_module.SCRUB_IDS}')
        SCRUB_IDS.update(scenario_module.SCRUB_IDS)

    LOGGER.debug('starting script')
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    if not os.path.exists(WORK_STATUS_DATABASE_PATH):
        _create_work_table_schema(WORK_STATUS_DATABASE_PATH)

    task_graph = taskgraph.TaskGraph(
        WORKSPACE_DIR, args.n_workers)
    os.makedirs(ECOSHARD_DIR, exist_ok=True)
    ecoshard_path_map = {}
    LOGGER.info('scheduling downloads')
    LOGGER.debug('starting downloads')
    for ecoshard_id, ecoshard_url in ECOSHARDS.items():
        ecoshard_path = os.path.join(
            ECOSHARD_DIR, os.path.basename(ecoshard_url))
        download_task = task_graph.add_task(
            func=ecoshard.download_url,
            args=(ecoshard_url, ecoshard_path),
            target_path_list=[ecoshard_path])
        ecoshard_path_map[ecoshard_id] = ecoshard_path
    LOGGER.info('waiting for downloads to finish')
    task_graph.join()

    # global DEM that's used
    task_graph.add_task(
        func=unzip_and_build_dem_vrt,
        args=(
            ecoshard_path_map[DEM_ID], ECOSHARD_DIR, DEM_TILE_DIR,
            DEM_VRT_PATH),
        target_path_list=[DEM_VRT_PATH],
        task_name='build DEM vrt')

    watershed_dir = os.path.join(
        ECOSHARD_DIR, 'watersheds_globe_HydroSHEDS_15arcseconds')
    expected_watershed_path = os.path.join(
        watershed_dir, 'af_bas_15s_beta.shp')

    task_graph.add_task(
        func=unzip,
        args=(ecoshard_path_map[WATERSHED_ID], ECOSHARD_DIR),
        target_path_list=[expected_watershed_path],
        task_name='unzip watersheds')
    LOGGER.debug('waiting for downloads and data to construct')
    task_graph.join()
    invalid_value_task_list = []
    LOGGER.debug('scheduling scrub of requested data')
    os.makedirs(SCRUB_DIR, exist_ok=True)
    for ecoshard_id_to_scrub in SCRUB_IDS:
        ecoshard_path = ecoshard_path_map[ecoshard_id_to_scrub]
        scrub_path = os.path.join(SCRUB_DIR, os.path.basename(ecoshard_path))
        task_graph.add_task(
            func=scrub_raster,
            args=(ecoshard_path, scrub_path),
            target_path_list=[scrub_path],
            task_name=f'scrub {ecoshard_path}')
        ecoshard_path_map[ecoshard_id_to_scrub] = scrub_path
    LOGGER.debug('wait for scrubbing to end')
    task_graph.join()
    LOGGER.debug('done with scrub, check for dirty rasters')
    checked_path_set = set()  # could have different id but same raster
    for ecoshard_id, ecoshard_path in ecoshard_path_map.items():
        if ecoshard_path in checked_path_set:
            continue
        if (pygeoprocessing.get_gis_type(ecoshard_path) ==
                pygeoprocessing.RASTER_TYPE):
            LOGGER.debug(f'checking {ecoshard_id} {ecoshard_path}')
            invalid_value_task = task_graph.add_task(
                func=detect_invalid_values,
                args=(ecoshard_path,),
                store_result=True,
                task_name=f'detect invalid values in {ecoshard_path}')
            invalid_value_task_list.append(
                (ecoshard_id, invalid_value_task))
            checked_path_set.add(ecoshard_path)
    invalid_raster_list = []
    for ecoshard_id, invalid_value_task in invalid_value_task_list:
        invalid_value_result = invalid_value_task.get()
        if invalid_value_result is not True:
            invalid_raster_list.append(
                (ecoshard_id, invalid_value_result))
    if invalid_raster_list:
        raise ValueError(
            f'invalid rasters at ' +
            '\n'.join([str(x) for x in invalid_raster_list]))

    LOGGER.debug('schedule watershed work')
    watershed_path_from_base = {}
    for watershed_path in glob.glob(os.path.join(watershed_dir, '*.shp')):
        watershed_basename = os.path.basename(
            os.path.splitext(watershed_path)[0])
        watershed_path_from_base[watershed_basename] = watershed_path
        watershed_vector = gdal.OpenEx(watershed_path, gdal.OF_VECTOR)
        watershed_layer = watershed_vector.GetLayer()
        local_watershed_process_list = [
            (_create_watershed_id(
                watershed_path, watershed_feature.GetFID())[1],
             watershed_feature.GetGeometryRef().Area())
            for watershed_feature in watershed_layer
            if watershed_feature.GetGeometryRef().Area() >
            AREA_DEG_THRESHOLD]
        # The IGNORE is if it's already in there, keep the status as whatever
        schedule_watershed_sql = '''
            INSERT OR IGNORE INTO
                work_status(
                    scenario_id, watershed_id, watershed_area, status)
            VALUES(?, ?, ?, ?);
        '''
        for scenario_id in SCENARIOS:
            # schedule all the watersheds that are large enough per scenario
            # for this particular watershed path
            argument_list = [
                (scenario_id, watershed_id, watershed_area,
                 SCHEDULED_STATUS) for (watershed_id, watershed_area)
                in local_watershed_process_list]
            _execute_sqlite(
                schedule_watershed_sql, WORK_STATUS_DATABASE_PATH,
                argument_list=argument_list,
                mode='modify', execute='executemany')
        watershed_layer = None
        watershed_vector = None

    LOGGER.info(f'starting watershed status logger')
    report_watershed_thread = threading.Thread(
        target=_report_watershed_count)
    report_watershed_thread.daemon = True
    report_watershed_thread.start()

    manager = multiprocessing.Manager()
    stitch_worker_list = []
    stitch_queue_list = []
    target_raster_list = []
    for scenario_id, scenario_vars in SCENARIOS.items():
        eff_n_lucode_map, load_n_lucode_map = load_biophysical_table(
            ecoshard_path_map[scenario_vars['biophysical_table_id']],
            BIOPHYSICAL_TABLE_IDS[scenario_vars['biophysical_table_id']])

        # make a stitcher for this scenario for export and modified load
        stitch_queue = manager.Queue()
        stitch_queue_list.append(stitch_queue)
        target_export_raster_path = os.path.join(
            WORKSPACE_DIR, f'{scenario_id}_{TARGET_CELL_LENGTH_M:.1f}_{ROUTING_ALGORITHM}_export.tif')
        target_modified_load_raster_path = os.path.join(
            WORKSPACE_DIR, f'{scenario_id}_{TARGET_CELL_LENGTH_M:.1f}_{ROUTING_ALGORITHM}_modified_load.tif')

        # create the empty rasters if they don't exist
        if not os.path.exists(target_export_raster_path):
            create_empty_wgs84_raster(
                BASE_WGS84_LENGTH_DEG, -1, target_export_raster_path)
        if not os.path.exists(target_modified_load_raster_path):
            create_empty_wgs84_raster(
                BASE_WGS84_LENGTH_DEG, -1, target_modified_load_raster_path)

        target_raster_list.extend(
            [target_export_raster_path, target_modified_load_raster_path])

        stitch_worker_thread = threading.Thread(
            target=stitch_worker,
            args=(
                scenario_id, target_export_raster_path,
                target_modified_load_raster_path, stitch_queue,
                args.watersheds is None))
        stitch_worker_thread.start()
        stitch_worker_list.append(stitch_worker_thread)

        watersheds_to_process_query = '''
            SELECT watershed_id FROM work_status
            WHERE scenario_id=? AND status!=?
            ORDER BY watershed_area DESC;'''

        if args.watersheds:
            # make it it a tuple so it matches the sqlite query
            watershed_id_work_list = [
                (watershed_id,) for watershed_id in args.watersheds]
        else:
            watershed_id_work_list = _execute_sqlite(
                watersheds_to_process_query, WORK_STATUS_DATABASE_PATH,
                argument_list=[scenario_id, COMPLETE_STATUS],
                mode='read_only', execute='execute', fetch='all')

        last_time = time.time()
        for watershed_index, (watershed_id,) in enumerate(
                watershed_id_work_list):
            if time.time()-last_time > 15:
                LOGGER.debug(
                    f'schedulding {watershed_index} of '
                    f'{len(watershed_id_work_list)} '
                    f'{100*watershed_index/(len(watershed_id_work_list)-1):.1f}% complete')
                last_time = time.time()
            watershed_basename, watershed_fid = _split_watershed_id(
                watershed_id)
            watershed_path = os.path.join(
                watershed_dir, f'{watershed_basename}.shp')
            watershed_vector = gdal.OpenEx(watershed_path, gdal.OF_VECTOR)
            local_workspace_dir = os.path.join(
                WORKSPACE_DIR, scenario_id, watershed_id)
            local_export_raster_path = os.path.join(
                local_workspace_dir, os.path.basename(
                    target_export_raster_path))
            local_modified_load_raster_path = os.path.join(
                local_workspace_dir, os.path.basename(
                    target_modified_load_raster_path))
            task_graph.add_task(
                func=ndr_plus_and_stitch,
                args=(
                    scenario_id,
                    watershed_path_from_base[watershed_basename],
                    watershed_fid,
                    TARGET_CELL_LENGTH_M,
                    RETENTION_LENGTH_M,
                    K_VAL,
                    FLOW_THRESHOLD,
                    MAX_PIXEL_FILL_COUNT,
                    ROUTING_ALGORITHM,
                    DEM_VRT_PATH,
                    ecoshard_path_map[scenario_vars['lulc_id']],
                    ecoshard_path_map[scenario_vars['precip_id']],
                    ecoshard_path_map[scenario_vars['fertilizer_id']],
                    eff_n_lucode_map,
                    load_n_lucode_map,
                    local_export_raster_path,
                    local_modified_load_raster_path,
                    local_workspace_dir,
                    stitch_queue),
                task_name=f'{watershed_basename}_{watershed_fid}')
        LOGGER.info(f'waiting for scenario {scenario_id} to finish.')
        task_graph.join()
        stitch_queue.put(None)
        LOGGER.debug(
            f'joining stitch worker thread for scenario {scenario_id}')
        stitch_worker_thread.join()

    LOGGER.debug('ALL DONE!')


def upsample_compress_and_overview(
        base_raster_path, upsampled_raster_path, target_raster_path):
    """Compress and overview base to raster."""
    ecoshard.convolve_layer(
        base_raster_path, 2, 'sum', upsampled_raster_path)
    ecoshard.compress_raster(upsampled_raster_path, target_raster_path)
    ecoshard.build_overviews(target_raster_path)


if __name__ == '__main__':
    main()
