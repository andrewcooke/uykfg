
from os.path import join

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.expression import func, select
from sqlalchemy.types import Integer, Boolean, UnicodeText

from uykff.core.db.support import Base


ALBUMS, TRACKS = 'albums', 'tracks'


class __Common(Base):

    __abstract__ = True
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)

    @classmethod
    def count(cls, session):
        return session.connection().execute(select([func.count(cls.id)])).scalar()


class Collection(__Common):

    __tablename__ = 'collections'
    path = Column(UnicodeText)


class Artist(__Common):

    __tablename__ = 'artists'


class Album(__Common):

    __tablename__ = ALBUMS
    album_artist_id = Column(Integer, ForeignKey(Artist.id))
    album_artist = relationship(Artist, backref=ALBUMS)
    path = Column(UnicodeText)
    collection_id = Column(Integer, ForeignKey(Collection.id))
    collection = relationship(Collection, backref=ALBUMS)


class Track(__Common):

    __tablename__ = TRACKS
    artist_id = Column(Integer, ForeignKey(Artist.id))
    artist = relationship(Artist, backref=TRACKS)
    album_id = Column(Integer, ForeignKey(Album.id))
    album = relationship(Album, backref=TRACKS)
    path = Column(UnicodeText)
    collection_id = Column(Integer, ForeignKey(Collection.id))
    collection = relationship(Collection, backref=TRACKS)

    def __str__(self):
        return '%s: %s (%s)' % (self.artist.name, self.name, self.album.name)
