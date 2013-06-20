#!/bin/bash

cd ~/project/uykfg
source env/bin/activate
PYTHONPATH=src python3 src/uykfg/play.py 2>&1 | egrep --line-buffered -v ":mpd" > ~/log/uykfg-play.log &
#tail -f ~/log/uykfg-play.log
