#!/bin/bash

rm -fr env
virtualenv --python=python3.3 env
source env/bin/activate
easy_install sqlalchemy
easy_install stagger
easy_install nose
easy_install python-mpd2

