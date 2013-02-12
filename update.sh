#!/bin/bash

cd ~/project/uykfg
source env/bin/activate
PYTHONPATH=src python src/uykfg/scan.py > ~/log/uykfg-scan.log 2>&1
PYTHONPATH=src python src/uykfg/link.py > ~/log/uykfg-link.log 2>&1
CNX=`egrep "cache (expired|miss) " ~/log/uykfg-scan.log ~/log/uykfg-link.log | wc -l`
if [[ $CNX -gt 0 ]]
then
    echo "$CNX connections"
fi
