
from logging import debug
from sys import argv

from sqlalchemy import not_

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Track, Artist
from uykfg.support.configure import Config


def who(names):
    config = Config.default()
    session = startup(config)
    artists = session.query(Artist.id)
    for name in names:
        debug('filtering by %s' % name)
        artists = session.query(Artist.id).join(Artist.tags)
        if name.startswith('-'):
            artists = artists.filter(Artist.id.in_(artists), not_(Artist.tags.any(text=name[1:])))
        else:
            artists = artists.filter(Artist.id.in_(artists), Artist.tags.any(text=name))
    for artist in session.query(Artist).filter(Artist.id.in_(artists)).order_by(Artist.name):
        print(artist.name)


if __name__ == '__main__':
    who(argv[1:])

