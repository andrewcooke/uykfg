#!/bin/bash

source env/bin/activate
PYTHONPATH=src python src/uykfg/scan.py > ~/log/uykfg-scan.log 2>&1
PYTHONPATH=src python src/uykfg/link.py > ~/log/uykfg-link.log 2>&1

