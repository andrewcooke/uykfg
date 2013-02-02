
from uykfg.core.support.configure import Config
from uykfg.core.db import startup as db_startup


def main(config):
    db_startup(config)
    # TODO


if __name__ == '__main__':
    main(Config())
