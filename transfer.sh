#!/bin/bash

if [ $# -ne 2 ]
then
    echo
    echo "Create links in PATH to given size."
    echo
    echo "Usage:"
    echo "  $0 PATH SIZE_GB"
    echo
    exit 1
fi

if [ `ls "$1" | wc` ]
then
    echo "$1 contains data"
    exit 1
else
    mkdir -p "$1"
fi

source env/bin/activate
PYTHONPATH=src python3 src/uykfg/transfer.py $1 $2 2>&1 > ~/log/uykfg-transfer.log &
