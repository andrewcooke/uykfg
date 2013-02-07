#!/bin/bash

source env/bin/activate
PYTHONPATH=src python src/uykfg/link.py > ~/log/uykfg-link.log 2>&1 &
tail -f ~/log/uykfg-link.log
