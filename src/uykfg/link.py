
from uykfg.music.db import startup
from uykfg.music.link import link_all
from uykfg.support.configure import Config


def link():
    config = Config.default()
    session = startup(config)
    link_all(session, None)


if __name__ == '__main__':
    link()
