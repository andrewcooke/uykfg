
from uykfg.music.db import startup
from uykfg.music.scan import scan_all
from uykfg.nest.finder import Finder
from uykfg.support.configure import Config


def scan():
    config = Config.default()
    session = startup(config)
    finder = Finder(config, session)
    scan_all(session, finder, config)


if __name__ == '__main__':
    scan()