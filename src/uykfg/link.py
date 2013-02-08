
from uykfg.music.db import startup
from uykfg.music.link import link_all
from uykfg.nest.linker import Linker
from uykfg.support.configure import Config


def link():
    config = Config.default()
    session = startup(config)
    linker = Linker(config, session)
    link_all(session, linker, config)


if __name__ == '__main__':
    link()
