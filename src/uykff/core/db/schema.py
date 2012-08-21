
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.expression import func, select
from sqlalchemy.types import Integer, Boolean, UnicodeText


Base = declarative_base()


class Common(Base):

    __abstract__ = True

    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)

    @classmethod
    def count(cls, session):
        return session.connection().execute(select([func.count(cls.id)])).scalar()


class Artist(Common):

    __tablename__ = 'artists'


class Album(Common):

    __tablename__ = 'albums'
    path = Column(UnicodeText)
    album_artist_id = Column(Integer, ForeignKey(Artist.id), nullable=True)
    album_artist = relationship(Artist, backref='albums')


class Track(Common):

    __tablename__ = 'tracks'
    artist_id = Column(Integer, ForeignKey(Artist.id))
    artist = relationship(Artist, backref='tracks')
    album_id = Column(Integer, ForeignKey(Album.id))
    album = relationship(Album, backref='tracks')
    path = Column(UnicodeText)

    def __str__(self):
        return '%s: %s (%s)' % (self.artist.name, self.name, self.album.name)


