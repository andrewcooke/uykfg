#!/bin/bash

source env/bin/activate
PYTHONPATH=src python src/uykfg/play.py 2>&1 | egrep --line-buffered -v ":mpd" > ~/log/uykfg-play.log &
tail -f ~/log/uykfg-play.log
