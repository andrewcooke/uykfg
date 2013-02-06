
from unittest import TestCase

from uykfg.music.db import startup
from uykfg.nest.db import NestArtist
from uykfg.nest.finder import Finder, FinderError
from uykfg.support.configure import Config


class FinderTest(TestCase):

    def finder(self):
        config = Config.default()
        session = startup(config)
        return session, Finder(config, session)

    def assert_artist(self, session, artist, music_name, nest_name):
        assert artist.name == music_name, artist.name
        nest_artist = session.query(NestArtist).filter(NestArtist.name == nest_name).one()
        assert nest_artist.name == nest_name, nest_artist.name
        assert nest_artist.artist == artist

    def test_track(self):
        session, finder = self.finder()
        artist = finder.find_track_artist(session, 'Miles', 'Blue')
        self.assert_artist(session, artist, 'Miles', 'Miles Davis')

    def test_artist(self):
        session, finder = self.finder()
        artist = finder.find_artist(session, 'Miles')
        self.assert_artist(session, artist, 'Miles', 'Miles')

    def test_tracks(self):
        session, finder = self.finder()
        artist = finder.find_tracks_artist(session, 'Miles', ['So What', 'All Blues', 'Noise'])
        self.assert_artist(session, artist, 'Miles', 'Miles Davis')

    def test_bad(self):
        session, finder = self.finder()
        try:
            finder.find_track_artist(session, 'XUSAIH', 'xaSXSA')
            assert False, 'Expected failure'
        except FinderError:
            pass
