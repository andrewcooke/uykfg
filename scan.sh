#!/bin/bash

source env/bin/activate
PYTHONPATH=src python src/uykfg/scan.py > ~/log/uykfg-scan.log 2>&1 &
tail -f ~/log/uykfg-scan.log

