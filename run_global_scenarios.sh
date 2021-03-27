#!/bin/bash

for scenario_id in restoration sustainable_currentpractices
do
    docker run -it --rm -v `pwd`:/usr/local/workspace --name ndr_$scenario_id --shm-size=32gb therealspring/inspring:latest global_ndr_plus_pipeline.py scenarios.nci_global --limit_to_scenarios $scenario_id
done
