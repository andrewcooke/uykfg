
from time import time
from unittest import TestCase

from uykfg.core.db import startup
from uykfg.core.db.catalogue import Track, Artist, Album
from uykfg.core.support.configure import Config


class TestCatalogue(TestCase):

    def test_catalogue(self):

        Session = startup(Config(db_url='sqlite:///'))

        session = Session()
        artist = Artist(name='bob', tagger_name='tagger', tag_id=0)
        session.add(artist)
        track1 = Track(name='track1', artist=artist, number='1', file='file1', modified=time())
        session.add(track1)
        track2 = Track(name='track2', artist=artist, number='2', file='file2', modified=time())
        session.add(track2)
        album = Album(name='album', tracks=[track1, track2])
        session.add(album)
        session.commit()

        session = Session()
        artists = session.query(Artist).all()
        assert len(artists) == 1, artists
        assert len(artists[0].tracks) == 2, artists[0].tracks
        tracks = session.query(Track).all()
        assert len(tracks) == 2, tracks
        albums = session.query(Album).all()
        assert len(albums) == 1, albums
        assert tracks[0].album == albums[0]

