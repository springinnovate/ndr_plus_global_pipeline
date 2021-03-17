"""CBD Global NDR scenario."""
# All links in this dict is an ecoshard that will be downloaded to
# ECOSHARD_DIR
ECOSHARD_PREFIX = 'https://storage.googleapis.com/'
WATERSHED_ID = 'hydrosheds_15arcseconds'
# Known properties of the DEM:

# Global properties of the simulation
RETENTION_LENGTH_M = 150
K_VAL = 1.0
TARGET_CELL_LENGTH_M = 300
FLOW_THRESHOLD = int(500**2*90 / TARGET_CELL_LENGTH_M**2)
ROUTING_ALGORITHM = 'D8'
TARGET_WGS84_LENGTH_DEG = 10/3600
BASE_WGS84_LENGTH_DEG = 10/3600/2
AREA_DEG_THRESHOLD = 0.000016 * 10  # this is 10 times larger than hydrosheds 1 "pixel" watersheds

BIOPHYSICAL_TABLE_IDS = {
    'esa_aries_rs3': 'Value',
    }

# ADD NEW DATA HERE
ECOSHARDS = {
    # Biophysical table:
    'esa_aries_rs3': f'{ECOSHARD_PREFIX}nci-ecoshards/nci-NDR-biophysical_table_ESA_ARIES_RS3_md5_74d69f7e7dc829c52518f46a5a655fb8.csv',
    # Precip:
    'worldclim_ssp3': f'{ECOSHARD_PREFIX}ipbes-ndr-ecoshard-data/precip_scenarios/he60pr50_md5_829fbd47b8fefb064ae837cbe4d9f4be.tif',
    # LULCs:
    'esacci-lc-l4-lccs-map-300m-p1y-2015-v2.0.7': f'{ECOSHARD_PREFIX}ipbes-ndr-ecoshard-data/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7_md5_1254d25f937e6d9bdee5779d377c5aa4.tif',
    'pnv_esa_iis': f'{ECOSHARD_PREFIX}ipbes-ndr-ecoshard-data/ESACCI_PNV_iis_OA_ESAclasses_max_ESAresproj_md5_e6575db589abb52c683d44434d428d80.tif',
    # Fertilizer
    'ag_load_ssp3': f'{ECOSHARD_PREFIX}ipbes-ndr-ecoshard-data/ag_load_scenarios/ssp3_2050_ag_load_md5_9fab631dfdae22d12cd92bb1983f9ef1.tif',
}

# put IDs here that need to be scrubbed, you may know these a priori or you
# may run the pipeline and see an error and realize you need to add them
SCRUB_IDS = {
    'worldclim_ssp3',
}

# DEFINE SCENARIOS HERE SPECIFYING 'lulc_id', 'precip_id', 'fertilizer_id', and 'biophysical_table_id'
# name the key of the scenario something unique
SCENARIOS = {
    'esa2015_driverssp3': {
        'lulc_id': 'esacci-lc-l4-lccs-map-300m-p1y-2015-v2.0.7',
        'precip_id': 'worldclim_ssp3',
        'fertilizer_id': 'ag_load_ssp3',
        'biophysical_table_id': 'esa_aries_rs3',
    },
    'pnv_driverssp3': {
        'lulc_id': 'pnv_esa_iis',
        'precip_id': 'worldclim_ssp3',
        'fertilizer_id': 'ag_load_ssp3',
        'biophysical_table_id': 'esa_aries_rs3',
    },
}
