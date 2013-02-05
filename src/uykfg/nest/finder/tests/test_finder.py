
from unittest import TestCase

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist
from uykfg.nest.db import NestArtist
from uykfg.nest.finder import Finder, FinderError
from uykfg.support.configure import Config


class FinderTest(TestCase):

    def finder(self):
        config = Config.default()
        Session = startup(config)
        return Session(), Finder(config, Session)

    def id3(self, artist, title):
        class Object: pass
        id3 = Object()
        id3.artist = artist
        id3.title = title
        return id3

    def assert_artist(self, session, artist, music_name, nest_name):
        assert artist.name == music_name, artist.name
        nest_artist = session.query(NestArtist).filter(NestArtist.name == nest_name).one()
        assert nest_artist.name == nest_name, nest_artist.name
        assert nest_artist.artist == artist

    def test_track(self):
        session, finder = self.finder()
        id3 = self.id3('Miles', 'Blue')
        artist = finder.find_artist(session, id3)
        self.assert_artist(session, artist, 'Miles', 'Miles Davis')

    def test_artist(self):
        session, finder = self.finder()
        id3 = self.id3('Miles', 'VCFGADSAY')
        artist = finder.find_artist(session, id3)
        self.assert_artist(session, artist, 'Miles', 'Miles')

    def test_bad(self):
        session, finder = self.finder()
        id3 = self.id3('YFSDFDS', 'VCFGADSAY')
        try:
            finder.find_artist(session, id3)
            assert False, 'Expected failure'
        except FinderError:
            pass
