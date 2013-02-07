#!/bin/bash

source env/bin/activate
PYTHONPATH=src python src/uykfg/play.py > ~/log/uykfg-play.log 2>&1 &
tail -f ~/log/uykfg-play.log
