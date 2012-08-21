
from uykff.core.config import Config
from uykff.core.db import startup as db_startup


def main(config):
    db_startup(config)


if __name__ == '__main__':
    main(Config())
