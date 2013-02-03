
from uykfg.support.configure import Config
from uykfg.music.db import startup as db_startup


def main(config):
    db_startup(config)
    # TODO


if __name__ == '__main__':
    main(Config())
