
from sys import argv

from uykfg.music.db import startup
from uykfg.music.transfer import transfer_size
from uykfg.support.configure import Config


def transfer(root, size):
    config = Config.default()
    session = startup(config)
    transfer_size(session, config, root, size)


if __name__ == '__main__':
    transfer(argv[1], argv[2])
