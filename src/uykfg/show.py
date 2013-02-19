
from sys import argv

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist
from uykfg.support.configure import Config


def show(names):
    config = Config.default()
    session = startup(config)
    for name in names:
        for artist in session.query(Artist).filter(Artist.name == name).all():
            print(artist.name)
            print(' tags:\n  %s' % ' '.join('"%s"' % tag.text for tag in artist.tags))


if __name__ == '__main__':
    show(argv[1:])
