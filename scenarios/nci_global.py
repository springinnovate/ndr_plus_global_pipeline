"""CBD Global NDR scenario."""
# All links in this dict is an ecoshard that will be downloaded to
# ECOSHARD_DIR
ECOSHARD_PREFIX = 'https://storage.googleapis.com/'

BIOPHYSICAL_TABLE_IDS = {
    'nci-ndr-biophysical_table_forestry_grazing': 'ID', }

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
    'grazing_expansion': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios0221_grazing_expansion_md5_140803bc8aef02a1742aa1d1757e9e76.tif',
    'restoration': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios0221_restoration_md5_16450b43f0a232b32a847c9738affda3.tif',
    'sustainable_current': f'{ECOSHARD_PREFIX}nci-ecoshards/one_last_run/scenarios0321_sustainable_current_md5_82afe022ffa8485a9b10154ee844b54f.tif',
    # Fertilizer
    'intensificationnapp_allcrops_irrigated_max_model_and_observednapprevb_bmps': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios050420/IntensificationNapp_allcrops_irrigated_max_Model_and_observedNappRevB_BMPs_md5_ddc000f7ce7c0773039977319bcfcf5d.tif',
    'intensificationnapp_allcrops_rainfed_max_model_and_observednapprevb_bmps': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios050420/IntensificationNapp_allcrops_rainfed_max_Model_and_observedNappRevB_BMPs_md5_fa2684c632ec2d0e0afb455b41b5d2a6.tif',
    'extensificationnapp_allcrops_rainfedfootprint_gapfilled_observednapprevb': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios050420/ExtensificationNapp_allcrops_rainfedfootprint_gapfilled_observedNappRevB_md5_1185e457751b672c67cc8c6bf7016d03.tif',
    'intensificationnapp_allcrops_irrigated_max_model_and_observednapprevb': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios050420/IntensificationNapp_allcrops_irrigated_max_Model_and_observedNappRevB_md5_9331ed220772b21f4a2c81dd7a2d7e10.tif',
    'intensificationnapp_allcrops_rainfed_max_model_and_observednapprevb': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios050420/IntensificationNapp_allcrops_rainfed_max_Model_and_observedNappRevB_md5_1df3d8463641ffc6b9321e73973f3444.tif',
}

# put IDs here that need to be scrubbed, you may know these a priori or you
# may run the pipeline and see an error and realize you need to add them
SCRUB_IDS = {
}

# DEFINE SCENARIOS HERE SPECIFYING 'lulc_id', 'precip_id', 'fertilizer_id', and 'biophysical_table_id'
# name the key of the scenario something unique
SCENARIOS = {
    'extensification_bmps_irrigated': {
        'lulc_id': 'extensification_bmps_irrigated',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_allcrops_irrigated_max_model_and_observednapprevb_bmps',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'extensification_bmps_rainfed': {
        'lulc_id': 'extensification_bmps_rainfed',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_allcrops_rainfed_max_model_and_observednapprevb_bmps',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'extensification_current_practices': {
        'lulc_id': 'extensification_current_practices',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'extensificationnapp_allcrops_rainfedfootprint_gapfilled_observednapprevb',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'extensification_intensified_irrigated': {
        'lulc_id': 'extensification_intensified_irrigated',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_allcrops_irrigated_max_model_and_observednapprevb',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'extensification_intensified_rainfed': {
        'lulc_id': 'extensification_intensified_rainfed',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_allcrops_rainfed_max_model_and_observednapprevb',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'fixedarea_bmps_irrigated': {
        'lulc_id': 'fixedarea_bmps_irrigated',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_allcrops_irrigated_max_model_and_observednapprevb_bmps',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'fixedarea_bmps_rainfed': {
        'lulc_id': 'fixedarea_bmps_rainfed',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_allcrops_rainfed_max_model_and_observednapprevb_bmps',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'fixedarea_intensified_irrigated': {
        'lulc_id': 'fixedarea_intensified_irrigated',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_allcrops_irrigated_max_model_and_observednapprevb',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'fixedarea_intensified_rainfed': {
        'lulc_id': 'fixedarea_intensified_rainfed',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'intensificationnapp_allcrops_irrigated_max_model_and_observednapprevb',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'grazing_expansion': {
        'lulc_id': 'grazing_expansion',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'extensificationnapp_allcrops_rainfedfootprint_gapfilled_observednapprevb',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'restoration': {
        'lulc_id': 'restoration',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'extensificationnapp_allcrops_rainfedfootprint_gapfilled_observednapprevb',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
    'sustainable_currentpractices': {
        'lulc_id': 'sustainable_current',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'extensificationnapp_allcrops_rainfedfootprint_gapfilled_observednapprevb',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
}
