
from logging import debug
from sys import argv
from sqlalchemy import alias

from sqlalchemy.sql.functions import random

from uykfg.mpd_.add import add_tracks
from uykfg.music.db import startup
from uykfg.music.db.catalogue import Track, Artist
from uykfg.music.db.tags import Tag
from uykfg.support.configure import Config


def add(count, names):
    config = Config.default()
    session = startup(config)
    tracks = session.query(Track)
    for name in names:
        artist = alias(Artist)
        tracks = tracks.join(artist).join(artist.tags).filter(artist.tags.any(name))
    tracks = tracks.order_by(random()).limit(count)
    add_tracks(session, config, tracks.all())


if __name__ == '__main__':
    count = 1
    names = argv[1:]
    assert names
    if len(names) > 1:
        try:
            count = int(names[0])
            names.pop(0)
        except ValueError: pass
    add(count, names)

