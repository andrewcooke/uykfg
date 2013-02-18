
from logging import warning, info
from sys import argv
from sqlalchemy import or_

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist, Track, Album
from uykfg.music.db.network import Link
from uykfg.support.configure import Config


def drop(name):
    warning('deleting %s' % name)
    config = Config.default()
    session = startup(config)
    for artist in session.query(Artist).filter(Artist.name == name).all():
        for track in session.query(Track).filter(Track.artist_id == artist.id).all():
            info('deleting %s from %s' % (track.name, track.album))
            session.delete(track)
        session.commit()
    artists = session.query(Artist).outerjoin(Track).filter(Artist.id == Track.artist_id, Track.id == None)
    info('deleting %d unused artists' % artists.count())
    for artist in artists.all():
        session.query(Link)\
            .filter(or_(Link.src == artist, Link.dst == artist)).delete()
    artists.delete()
    albums = session.query(Album).outerjoin(Track).filter(Track.id == None)
    info('deleting %d unused albums' % albums.count())
    albums.delete()
    session.commit()


if __name__ == '__main__':
    assert len(argv) == 2
    drop(argv[1])
