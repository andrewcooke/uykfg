#!/bin/bash

PARAMS=""
for PARAM in "$@"
do
  PARAMS="${PARAMS} \"${PARAM}\""
done
source env/bin/activate
bash -c "PYTHONPATH=src python src/uykfg/who.py $PARAMS"
