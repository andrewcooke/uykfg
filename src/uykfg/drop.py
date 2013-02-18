
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
            warning('deleting %s from %s' % (track.name, track.album))
            session.delete(track)
        session.commit()
    artists = session.query(Artist.id).outerjoin(Track)\
        .filter(Track.id == None)
    warning('deleting %d unused artists' % artists.count())
    for artist in artists.all():
        session.query(Link)\
            .filter(or_(Link.src == artist, Link.dst == artist)).delete()
    session.query(Artist).filter(Artist.id.in_(artists))\
        .delete(synchronize_session=False)
    albums = session.query(Album.id).outerjoin(Track).filter(Track.id == None)
    warning('deleting %d unused albums' % albums.count())
    session.query(Album).filter(Album.id.in_(albums))\
        .delete(synchronize_session=False)
    session.commit()


if __name__ == '__main__':
    assert len(argv) == 2
    drop(argv[1])
