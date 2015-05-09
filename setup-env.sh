#!/bin/bash

rm -fr env
virtualenv-3.4 --python=python3.4 env
source env/bin/activate
pip install sqlalchemy
#pip install stagger
pip install nose
pip install python-mpd2

