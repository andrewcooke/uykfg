
from sys import argv

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist
from uykfg.support.configure import Config


def show(name):
    config = Config.default()
    session = startup(config)
    for artist in session.query(Artist).filter(Artist.name == name).all():
        print(artist.name)
        for tag in artist.values:
            print(' %s' % tag.text)


if __name__ == '__main__':
    assert len(argv) == 2
    show(argv[1])
