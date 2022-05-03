"""CBD Global NDR scenario."""
import os

# All links in this dict is an ecoshard that will be downloaded to
# ECOSHARD_DIR
ECOSHARD_PREFIX = 'https://storage.googleapis.com/'

BIOPHYSICAL_TABLE_IDS = {
    'nci-ndr-biophysical_table_forestry_grazing': 'ID', }

SHERLOCK_SCRATCH = os.environ['SCRATCH']

# ADD NEW DATA HERE
ECOSHARDS = {
    # Biophysical table:
    'nci-ndr-biophysical_table_forestry_grazing': f'{ECOSHARD_PREFIX}nci-ecoshards/nci-NDR-biophysical_table_forestry_grazing_md5_7524f2996fcc929ddc3aaccde249d59f.csv',
    # Precip:
    'worldclim_2015': f'{ECOSHARD_PREFIX}ipbes-ndr-ecoshard-data/worldclim_2015_md5_16356b3770460a390de7e761a27dbfa1.tif',
    # LULCs:
    'extensification_bmps_irrigated': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios0620_extensification_bmps_irrigated_md5_997290bf56ad3776eb271c56d57367d6.tif',
    'extensification_bmps_rainfed': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios0620_extensification_bmps_rainfed_md5_5a6382881976ed041499e5c6cb61516d.tif',
    'extensification_current_practices': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios052320_extensification_current_practices_md5_8becc0d5210d023efac2be719f0200fb.tif',
    'extensification_intensified_irrigated': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios052320_extensification_intensified_irrigated_md5_dcd1c26add8262120ce63d7a101cedab.tif',
    'extensification_intensified_rainfed': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios052320_extensification_intensified_rainfed_md5_6d34b0c107ad5655815f7ae624173eb5.tif',
    'fixedarea_bmps_irrigated': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios0620_fixedarea_bmps_irrigated_md5_2734856be55518996059a9330304cc0e.tif',
    'fixedarea_bmps_rainfed': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios0620_fixedarea_bmps_rainfed_md5_ff56f75f23cedf8d9181c6c7af71cf23.tif',
    'fixedarea_intensified_irrigated': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios052320_fixedarea_intensified_irrigated_md5_0b96c3ff00696a454d6c2fffb2ee1415.tif',
    'fixedarea_intensified_rainfed': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios052320_fixedarea_intensified_rainfed_md5_ec3a78c825186a12c16f3f7442eb03f4.tif',
    'grazing_expansion_lulc': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios0221_grazing_expansion_md5_140803bc8aef02a1742aa1d1757e9e76.tif',
    'restoration_lulc': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios0221_restoration_md5_16450b43f0a232b32a847c9738affda3.tif',
    'sustainable_current': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios0321_sustainable_current_md5_82afe022ffa8485a9b10154ee844b54f.tif',

    # Fertilizer
    ## Section 1 - these were already commented out by the time I (JD) got here
    ## with the first runs on Sherlock in October, 2021.
    #'intensificationnapp_allcrops_irrigated_max_model_and_observednapprevb_bmps': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios050420/IntensificationNapp_allcrops_irrigated_max_Model_and_observedNappRevB_BMPs_md5_ddc000f7ce7c0773039977319bcfcf5d.tif',
    #'intensificationnapp_allcrops_rainfed_max_model_and_observednapprevb_bmps': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios050420/IntensificationNapp_allcrops_rainfed_max_Model_and_observedNappRevB_BMPs_md5_fa2684c632ec2d0e0afb455b41b5d2a6.tif',
    #'extensificationnapp_allcrops_rainfedfootprint_gapfilled_observednapprevb': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios050420/ExtensificationNapp_allcrops_rainfedfootprint_gapfilled_observedNappRevB_md5_1185e457751b672c67cc8c6bf7016d03.tif',
    #'intensificationnapp_allcrops_irrigated_max_model_and_observednapprevb': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios050420/IntensificationNapp_allcrops_irrigated_max_Model_and_observedNappRevB_md5_9331ed220772b21f4a2c81dd7a2d7e10.tif',
    #'intensificationnapp_allcrops_rainfed_max_model_and_observednapprevb': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios050420/IntensificationNapp_allcrops_rainfed_max_Model_and_observedNappRevB_md5_1df3d8463641ffc6b9321e73973f3444.tif',

    ## Section 2 - these were the fertilizer application rasters used for the
    ## October, 2021 runs of NCI on Sherlock that I (JD) triggered.
    #'intensificationnapp_irrigated_bmps': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/finaltotalNfertratesirrigatedRevQ_BMPs_add_background_md5_a1bd38eaffd702079ab36c0bc46d770d.tif',
    #'intensificationnapp_rainfed_bmps': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/finaltotalNfertratesrainfedRevQ_BMPs_add_background_md5_b2232462adcae42eb8c1bf3403a0cf6b.tif',
    #'extensificationnapp_rainfedfootprint_gapfilled': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/finaltotalNfertratescurrentRevQ_add_background_md5_bd57fc740fe61b99133a4e22d3e89ece.tif',
    #'intensificationnapp_irrigated': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/finaltotalNfertratesirrigatedRevQ_add_background_md5_b763d688a87360d37868d6a0fbd6b68a.tif',
    #'intensificationnapp_rainfed': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/finaltotalNfertratesrainfedRevQ_add_background_md5_9f6a8dd89d25e4d7c413d268731a14f8.tif',

    ## Section 3 - these are the fertilizer application rasters that Peter made
    ## in early March, 2022 in response to Becky noticing that there was
    ## something wrong with the previous fertilizer rasters.
    ##
    ## These are located on the Sherlock $SCRATCH partition because Rich took
    ## over control of the ecoshards project on GCP and I can't just upload
    ## these ecoshards there at the moment.
    'intensificationnapp_irrigated_bmps': f'{SHERLOCK_SCRATCH}/nci-ecoshards/fertilizer-layers-2022-03-08/intensified_irrigated_n_app_bmps_md5_a773d463101ef827849ef847ddbbe881.tif',
    'intensificationnapp_rainfed_bmps': f'{SHERLOCK_SCRATCH}/nci-ecoshards/fertilizer-layers-2022-03-08/intensified_rainfed_n_app_bmps_md5_7637f211bb13a3ec66b00491d9518110.tif',
    'extensificationnapp_rainfedfootprint_gapfilled': f'{SHERLOCK_SCRATCH}/nci-ecoshards/finaltotalNfertratescurrentRevQ_add_background_md5_bd57fc740fe61b99133a4e22d3e89ece.tif',
    'intensificationnapp_irrigated': f'{SHERLOCK_SCRATCH}/nci-ecoshards/fertilizer-layers-2022-03-08/intensified_irrigated_n_app_md5_f472499f546b92835e8011b2654b253a.tif',
    'intensificationnapp_rainfed': f'{SHERLOCK_SCRATCH}/nci-ecoshards/fertilizer-layers-2022-03-08/intensified_rainfed_n_app_md5_48687737e6fdf931ddb163c6c9694e44.tif',

    # Section 4 - These are the additional LULCs that Rafa and Becky said
    # should be used for the Forestry, Grazing and Restoration scenarios.
    # These rasters are merely ecosharded versions of the rasters contained at
    # https://drive.google.com/drive/u/1/folders/13g52ihP7G2WrYuzl6-gO9yuCwhD3AEw-
    # The grazing_expansion_lulc and restoration_lulc were already ecosharded.
    'forestry_expansion_lulc': f'{SHERLOCK_SCRATCH}/nci-ecoshards/forestry_expansion_md5_215cd2a3db0c8a1a5451f395e87568ec.tif',
}

# JD sanity check to make sure these files exist.
for key, value in ECOSHARDS.items():
    if value.startswith(SHERLOCK_SCRATCH):
        assert os.path.exists(value)

# put IDs here that need to be scrubbed, you may know these a priori or you
# may run the pipeline and see an error and realize you need to add them
SCRUB_IDS = {
    'intensificationnapp_irrigated_bmps',
    'intensificationnapp_rainfed_bmps',
    'intensificationnapp_irrigated',
    'intensificationnapp_rainfed',
}

# DEFINE SCENARIOS HERE SPECIFYING 'lulc_id', 'precip_id', 'fertilizer_id', and 'biophysical_table_id'
# name the key of the scenario something unique
SCENARIOS = {
    'extensification_bmps_irrigated': {
        'lulc_id': 'extensification_bmps_irrigated',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_irrigated_bmps',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'extensification_bmps_rainfed': {
        'lulc_id': 'extensification_bmps_rainfed',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_rainfed_bmps',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'extensification_current_practices': {
        'lulc_id': 'extensification_current_practices',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'extensificationnapp_rainfedfootprint_gapfilled',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'extensification_intensified_irrigated': {
        'lulc_id': 'extensification_intensified_irrigated',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_irrigated',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'extensification_intensified_rainfed': {
        'lulc_id': 'extensification_intensified_rainfed',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_rainfed',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'fixedarea_bmps_irrigated': {
        'lulc_id': 'fixedarea_bmps_irrigated',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_irrigated_bmps',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'fixedarea_bmps_rainfed': {
        'lulc_id': 'fixedarea_bmps_rainfed',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_rainfed_bmps',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'fixedarea_intensified_irrigated': {
        'lulc_id': 'fixedarea_intensified_irrigated',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_irrigated',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'fixedarea_intensified_rainfed': {
        'lulc_id': 'fixedarea_intensified_rainfed',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_irrigated',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'forestry_expansion': {
        'lulc_id': 'forestry_expansion_lulc',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'extensificationnapp_rainfedfootprint_gapfilled',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'grazing_expansion': {
        'lulc_id': 'grazing_expansion_lulc',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'extensificationnapp_rainfedfootprint_gapfilled',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'restoration': {
        'lulc_id': 'restoration_lulc',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'extensificationnapp_rainfedfootprint_gapfilled',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'sustainable_currentpractices': {
        'lulc_id': 'sustainable_current',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'extensificationnapp_rainfedfootprint_gapfilled',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
}
