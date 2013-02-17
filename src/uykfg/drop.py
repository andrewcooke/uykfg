
from logging import warning, info
from sys import argv

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist, Track, Album
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


if __name__ == '__main__':
    assert len(argv) == 2
    drop(argv[1])
