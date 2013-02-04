
from logging import debug
from unittest import TestCase
from os import utime
from os.path import join

from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Album, Artist, Track
from uykfg.music.scan.scanner import scan
from uykfg.support.db import TableBase
from uykfg.support.configure import Config
from uykfg.support.io import parent
from uykfg.support.sequences import lfilter


class DummyFinder:

    def find_artist(self, session, id3):
        try:
            dummy = session.query(DummyArtist).join('artist').\
                filter(Artist.name==id3.artist).one()
        except NoResultFound:
            debug('creating dummy artist for %s' % id3.artist)
            dummy = DummyArtist()
            session.add(dummy)
        if dummy.artist:
            artist = dummy.artist
        else:
            try:
                artist = session.query(Artist).filter(Artist.name==id3.artist).one()
            except NoResultFound:
                debug('creating artist %s' % id3.artist)
                artist = Artist(name=id3.artist)
                session.add(artist)
            dummy.artist_id = artist.id
        return artist


class DummyArtist(TableBase):

    __tablename__ = 'test_artists'
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey(Artist.id), nullable=True)
    artist = relationship(Artist)



class ScannerTest(TestCase):

    def scan_directory(self, file):
        config = Config(mp3_path=join(parent(__file__), file), db_url='sqlite:///')
#        config = Config(mp3_path=join(parent(__file__), file), db_url='sqlite:////tmp/test.sql')
        session = startup(config)()
        scan(session, DummyFinder(), config)
        return session, config

    def test_empty(self):
        session, _ = self.scan_directory('empty')
        assert len(session.query(Track).all()) == 0

    def test_not_empty(self):
        session, _ = self.scan_directory('mp3s')
        albums = session.query(Album).join(Album.tracks).join(Track.artist).filter(Artist.name == 'Artist 1').all()
        assert len(albums) == 1, albums
        album = albums[0]
        assert album.path == join(parent(__file__), 'mp3s', 'Artist 1', 'Album 1'), album.path
        assert len(album.tracks) == 2, album.tracks
        tracks = lfilter(lambda t: t.number == 1, album.tracks)
        assert len(tracks) == 1, tracks
        track = tracks[0]
        tracks = session.query(Track).all()
        assert len(tracks) == 7, len(tracks)
        tracks = session.query(Track).join(Track.artist).filter(Track.number == 1, Artist.name == 'Artist 1').all()
        assert len(tracks) == 1, len(tracks)
        assert track == tracks[0]
        assert track.name == 'Track 1', track.name
        assert track.file == 'Artist 1 - 01 - Track 1.mp3', track.file
        artists = session.query(Artist).filter(Artist.name == 'Artist 1').all()
        assert len(artists) == 1, len(artists)
        artist = artists[0]
        assert track.artist == artist, track.artist
        assert artist.name == 'Artist 1', artist.name
        assert len(artist.tracks) == 2, len(artist.tracks)

    def test_changed(self):
        session, config = self.scan_directory('mp3s')
        tracks = session.query(Track).all()
        assert len(tracks) == 7, len(tracks)
        track1a = session.query(Track).join(Track.artist).filter(Track.number == 1, Artist.name == 'Artist 1').one()
        track2a = session.query(Track).join(Track.artist).filter(Track.number == 2, Artist.name == 'Artist 1').one()

        utime(join(track1a.album.path, track1a.file), None)
        scan(session, DummyFinder(), config)
        tracks = session.query(Track).all()
        assert len(tracks) == 7, len(tracks)
        track1b = session.query(Track).join(Track.artist).filter(Track.number == 1, Artist.name == 'Artist 1').one()
        track2b = session.query(Track).join(Track.artist).filter(Track.number == 2, Artist.name == 'Artist 1').one()
        assert track1a.modified != track1b.modified
        assert track2a.modified == track2b.modified
