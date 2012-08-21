
'''
Most things should be configured via the web interface, but the basic
parameters of database location, binding address and port need to be
fixed before starting.

We require a config file at UYKFF_DIR/.uykfrcf.  If UYKFF_DIR is undefined
then is it taken to be the user's home directory.  If the .uykffrc file is
missing it is created.  When read, all values must be present (defaults
are given in the created file).
'''

from configparser import ConfigParser
from logging import basicConfig
from io import StringIO
from sys import stderr
from os import environ
from os.path import expanduser, join, exists


UYKFF_DIR, HOME, UYKFFRC, UYKFFDB = 'UYKFF_DIR', '~', '.uykffrc', '.uykffdb'
WEB, PORT, ADDRESS = 'web', 'port', 'address'
DATABASE, URL = 'database', 'url'
LOG, LEVEL, DEBUG = 'log', 'level', 'debug'


class Config:

    def __init__(self, text=None):
        if text:
            self._read(StringIO(text))
        else:
            dir = environ.get(UYKFF_DIR, HOME)
            path = expanduser(join(dir, UYKFFRC))
            if not exists(path):
                self._write(dir, path)
            else:
                with open(path) as input: self._read(input)

    def _read(self, input):
        parser = ConfigParser()
        parser.read_file(input)
        basicConfig(level=parser.get(LOG, LEVEL).upper())
        self.web_port = int(parser.getint(WEB, PORT))
        self.web_address = parser.get(WEB, ADDRESS)
        self.db_url = parser.get(DATABASE, URL)

    def _write(self, dir, path):
        parser = ConfigParser()
        parser.add_section(LOG)
        parser.set(LOG, LEVEL, DEBUG)
        parser.add_section(WEB)
        parser.set(WEB, PORT, '9001')
        parser.set(WEB, ADDRESS, 'localhost')
        parser.add_section(DATABASE)
        parser.set(DATABASE, URL, 'sqlite:///%s' % expanduser(join(dir, UYKFFDB)))
        with open(path, 'w') as output: parser.write(output)
        print('''
A new configuration file has been created at %s
Please edit it and then restart
If you move the file elsewhere please define the environment variable %s
''' % (path, UYKFF_DIR), file=stderr)
        exit(1)
