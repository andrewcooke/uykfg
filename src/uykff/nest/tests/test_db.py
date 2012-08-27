
from unittest import TestCase

from sqlalchemy.orm.session import sessionmaker

from uykff.core.db import startup
from uykff.core.db.catalogue import Artist
from uykff.core.support.configure import Config
from uykff.nest import NestTagger
from uykff.nest.db import NestArtist


class DbTest(TestCase):

    def test_db(self):

        Session = startup(Config(db_url='sqlite:///', modules=['uykff.nest']))

        session = Session()
        nest_artist = NestArtist()
        session.add(nest_artist)
        session.commit()

        artist = Artist(name='bob',
            tagger_name=NestTagger.TAGGER_NAME, tag_id=nest_artist.id)
        nest_artist.artist = artist
        session.add(artist)
        session.commit()

        session = Session()
        artists = session.query(Artist).all()
        assert len(artists) == 1, artists
        nest_artists = session.query(NestArtist).all()
        assert len(nest_artists) == 1, nest_artists
        assert nest_artists[0].artist == artists[0]

