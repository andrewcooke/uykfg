
from datetime import datetime
from importlib import import_module
from os.path import abspath, dirname, getmtime


def parent(path):
    return dirname(abspath(path))

def module_parent(name):
    return parent(import_module(name).__file__)

def getmdatetime(path):
    return datetime.fromtimestamp(getmtime(path))