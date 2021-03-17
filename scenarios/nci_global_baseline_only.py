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
    'esacci-lc-l4-lccs-map-300m-p1y-2015-v2.0.7': f'{ECOSHARD_PREFIX}ipbes-ndr-ecoshard-data/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7_md5_1254d25f937e6d9bdee5779d377c5aa4.tif',
    # Fertilizer
    'extensificationnapp_allcrops_rainfedfootprint_gapfilled_observednapprevb': f'{ECOSHARD_PREFIX}nci-ecoshards/scenarios050420/ExtensificationNapp_allcrops_rainfedfootprint_gapfilled_observedNappRevB_md5_1185e457751b672c67cc8c6bf7016d03.tif',
}

# put IDs here that need to be scrubbed, you may know these a priori or you
# may run the pipeline and see an error and realize you need to add them
SCRUB_IDS = {
}

# DEFINE SCENARIOS HERE SPECIFYING 'lulc_id', 'precip_id', 'fertilizer_id', and 'biophysical_table_id'
# name the key of the scenario something unique
SCENARIOS = {
    'baseline_currentpractices': {
        'lulc_id': 'esacci-lc-l4-lccs-map-300m-p1y-2015-v2.0.7',
        'precip_id': 'worldclim_2015',
        'fertilizer_id': 'extensificationnapp_allcrops_rainfedfootprint_gapfilled_observednapprevb',
        'biophysical_table_id': 'nci-ndr-biophysical_table_forestry_grazing',
    },
}