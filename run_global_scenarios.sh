#!/bin/bash

for scenario_id in extensification_bmps_irrigated extensification_bmps_rainfed extensification_current_practices extensification_intensified_irrigated extensification_intensified_rainfed fixedarea_bmps_irrigated fixedarea_bmps_rainfed fixedarea_intensified_irrigated fixedarea_intensified_rainfed grazing_expansion restoration sustainable_currentpractices
do
    echo docker run -it --rm -v `pwd`:/usr/local/workspace --name ndr --shm-size=32gb therealspring/inspring:latest global_ndr_plus_pipeline.py scenarios.nci_global --limit_to_scenarios $scenario_id
done
