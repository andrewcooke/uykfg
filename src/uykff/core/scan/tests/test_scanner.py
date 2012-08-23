
from unittest import TestCase
from os import utime
from os.path import join

from sqlalchemy.orm.session import sessionmaker

from uykff.core.db import startup
from uykff.core.db.catalogue import Album, Artist, Track
from uykff.core.scan.scanner import scan
from uykff.core.support.configure import DummyConfig, Config
from uykff.core.support.io import parent
from uykff.core.support.sequences import lfilter


class ScannerTest(TestCase):

    def do_test(self, file):
        Config() # set debug logs
        config = DummyConfig(mp3_path=join(parent(__file__), file), db_url='sqlite:///')
        engine = startup(config)
        session = sessionmaker(engine)()
        scan(session, config)
        return session, config

    def test_empty(self):
        session, _ = self.do_test('empty')
        assert len(session.query(Track).all()) == 0

    def test_not_empty(self):
        session, _ = self.do_test('mp3s')
        albums = session.query(Album).all()
        assert len(albums) == 1, albums
        album = albums[0]
        assert album.path == join(parent(__file__), 'mp3s', 'Conexion Domeyko'), album.path
        assert len(album.tracks) == 13, album.tracks
        tracks = lfilter(lambda t: t.number == 1, album.tracks)
        assert len(tracks) == 1, tracks
        track = tracks[0]
        tracks = session.query(Track).all()
        assert len(tracks) == 13, len(tracks)
        tracks = session.query(Track).filter(Track.number == 1).all()
        assert len(tracks) == 1, len(tracks)
        assert track == tracks[0]
        assert track.name == 'Habitantes', track.name
        assert track.file == 'Ud. No! - 01 - Habitantes.mp3', track.file
        artists = session.query(Artist).all()
        assert len(artists) == 1, len(artists)
        artist = artists[0]
        assert track.artist == artist, track.artist
        assert artist.name == 'Ud. No!', artist.name
        assert len(artist.tracks) == 13, len(artist.tracks)

    def test_changed(self):
        session, config = self.do_test('mp3s')
        tracks = session.query(Track).all()
        assert len(tracks) == 13, len(tracks)
        track1a = session.query(Track).filter(Track.number == 1).one()
        track2a = session.query(Track).filter(Track.number == 2).one()
        utime(join(track1a.album.path, track1a.file), None)
        scan(session, config)
        tracks = session.query(Track).all()
        assert len(tracks) == 13, len(tracks)
        track1b = session.query(Track).filter(Track.number == 1).one()
        track2b = session.query(Track).filter(Track.number == 2).one()
        assert track1a.modified != track1b.modified
        assert track2a.modified == track2b.modified
