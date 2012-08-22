
from uykff.core.support.configure import Config
from uykff.core.db import startup as db_startup
from uykff.core.root import startup as root_startup


def main(config):
    db_startup(config)
    root_startup(config)


if __name__ == '__main__':
    main(Config())
