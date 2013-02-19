#!/bin/bash

PARAMS=""
for PARAM in "$@"
do
  PARAMS="${PARAMS} \"${PARAM}\""
done
source env/bin/activate
PYTHONPATH=src python src/uykfg/drop.py $PARAMS

