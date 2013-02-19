
from logging import warning, info
from sys import argv

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist, Track, Album
from uykfg.music.scan import cull_artists, cull_albums
from uykfg.nest.finder import Finder
from uykfg.support.configure import Config


def drop(name):
    warning('deleting %s' % name)
    config = Config.default()
    session = startup(config)
    finder = Finder(config, session)
    for artist in session.query(Artist).filter(Artist.name == name).all():
        for track in session.query(Track).filter(Track.artist_id == artist.id).all():
            warning('deleting %s from %s' % (track.name, track.album))
            session.delete(track)
        session.commit()
    cull_artists(session, finder)
    cull_albums(session)


if __name__ == '__main__':
    assert len(argv) == 2, repr(argv)
    drop(argv[1])
