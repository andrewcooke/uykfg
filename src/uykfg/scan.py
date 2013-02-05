
from uykfg.music.db import startup
from uykfg.music.scan.scanner import scan_all
from uykfg.nest.finder import Finder
from uykfg.support.configure import Config


def scan():
    config = Config.default()
    Session = startup(config)
    finder = Finder(config, Session)
    scan_all(Session(), finder, config)


if __name__ == '__main__':
    scan()