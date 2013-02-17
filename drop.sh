#!/bin/bash

source env/bin/activate
PYTHONPATH=src python src/uykfg/drop.py $@
