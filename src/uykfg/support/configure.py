
'''
We require a config file at UYKFG_DIR/.uykfgrc.  If UYKFG_DIR is undefined
then is it taken to be the user's home directory.  If the .uykfgrc file is
missing it is created.  When read, all values must be present (defaults
are given in the created file).
'''

from configparser import ConfigParser
from importlib import import_module
from logging import basicConfig
from io import StringIO
from sys import stderr
from os import environ
from os.path import expanduser, join, exists, abspath


UYKFG_DIR, HOME, UYKFGRC, UYKFGDB = 'UYKFFG_DIR', '~', '.uykfgrc', '.uykfgdb'
DATABASE, URL, MAX_LINKS = 'database', 'url', 'max_links'
MP3, PATH = 'mp3', 'path'
LOG, LEVEL, DEBUG = 'log', 'level', 'debug'
ECHONEST, API_KEY = 'echonest', 'api_key'


class ConfigException(Exception):
    pass


class Config:

    def __init__(self, log_level='debug',
                 db_url='sqlite:///%s' % expanduser(join(environ.get(UYKFG_DIR, HOME), UYKFGDB)),
                 max_links=4, mp3_path=expanduser('~/music'), api_key=None):
        self.log_level = log_level
        self.db_url = db_url
        self.max_links = int(max_links)
        self.mp3_path = mp3_path
        self.api_key = api_key
        basicConfig(level=log_level.upper())

    @staticmethod
    def from_text(text):
        return Config.from_fp(StringIO(text), name='text')

    @staticmethod
    def from_file(path):
        with open(path) as input: return Config.from_fp(input, name=path)

    @staticmethod
    def from_fp(fp, name=None):
        name = name or fp.name
        try:
            parser = ConfigParser()
            parser.read_file(fp)
            return Config(log_level=parser.get(LOG, LEVEL),
                db_url = parser.get(DATABASE, URL),
                max_links = parser.get(DATABASE, MAX_LINKS),
                mp3_path = abspath(expanduser(parser.get(MP3, PATH))),
                api_key = parser.get(ECHONEST, API_KEY))
        except Exception as e:
            raise ConfigException('Error reading %s: %s' % (name, e))

    @staticmethod
    def default():
        dir = environ.get(UYKFG_DIR, HOME)
        path = expanduser(join(dir, UYKFGRC))
        if not exists(path):
            Config()._write_default(path)
        else:
            return Config.from_file(path)

    def _write_default(self, path):
        parser = ConfigParser()
        parser.add_section(LOG)
        parser.set(LOG, LEVEL, self.log_level)
        parser.add_section(DATABASE)
        parser.set(DATABASE, URL, self.db_url)
        parser.set(DATABASE, MAX_LINKS, str(self.max_links))
        parser.add_section(MP3)
        parser.set(MP3, PATH, self.mp3_path)
        parser.add_section(ECHONEST)
        parser.set(ECHONEST, API_KEY, '')
        with open(path, 'w') as output: parser.write(output)
        print('''
A new configuration file has been created at %s
Please edit it and then restart
If you move the file elsewhere please define the environment variable %s
''' % (path, UYKFG_DIR), file=stderr)
        exit(1)
