
from sys import argv

from uykfg.music.db import startup
from uykfg.music.scan import scan_all
from uykfg.nest.finder import Finder
from uykfg.support.configure import Config


def scan(all):
    config = Config.default()
    session = startup(config)
    finder = Finder(config, session)
    scan_all(session, finder, config, all)


if __name__ == '__main__':
    scan(len(argv) > 1)
