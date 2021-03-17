.. default-role:: code

Global NDR Plus Pipeline
========================

This code base contains a core processing pipeline to run NDR plus globally
and a set of scenario modules containing data to run them on.

To run the `cbd_scenario`:

```
docker container run --rm --name cbd -it -v `pwd`:/usr/local/workspace --shm-size=4gb therealspring/inspring:latest ./global_ndr_plus_pipeline.py scenarios.cbd_scenario
```

To run the `eu_bas_15s_beta_301360` and `eu_bas_15s_beta_301520` watersheds only:

```docker container run --rm --name cbd -it -v `pwd`:/usr/local/workspace --shm-size=4gb therealspring/inspring:latest ./cbd_global_ndr_plus.py scenarios.nci_global_baseline_only --watersheds eu_bas_15s_beta_301360 eu_bas_15s_beta_301520```

Available scenarios:

* `scenarios.cbd_scenario`: FILL IN DESCRIPTION
* `scenarios.nci_global`: FILL IN DESCRIPTION
* `scenarios.nci_global_baseline_only`: FILL IN DESCRIPTION
