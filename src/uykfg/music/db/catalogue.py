
'''
We assume that every album is in a separate directory, and that the
tracks are files within that directory.  Tracks have a single artist
(which may be a list of names etc).  We don't try to unify individuals
(artists are "groups", not "performers").

Different artists can have the same name.
'''

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Index
from sqlalchemy.sql.expression import func, select
from sqlalchemy.types import UnicodeText, Unicode, Integer, Boolean

from uykfg.support.db import TableBase


class __Common(TableBase):

    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(UnicodeText, nullable=False)

    @classmethod
    def count(cls, session):
        return session.connection().execute(select([func.count(cls.id)])).scalar()

    def __str__(self):
        return '%s (%d)' % (self.name, self.id)


class Artist(__Common):

    __tablename__ = 'music_artists'
    new = Column(Boolean, nullable=False, default=True)


class Album(__Common):

    __tablename__ = 'music_albums'
    path = Column(UnicodeText, nullable=False)

    def __str__(self):
        return '%s (%s)' % (self.name, self.path)


class Track(__Common):

    __tablename__ = 'music_tracks'
    artist_id = Column(Integer, ForeignKey(Artist.id), nullable=False)
    artist = relationship(Artist, backref='tracks')
    album_id = Column(Integer, ForeignKey(Album.id), nullable=False)
    album = relationship(Album, backref='tracks')
    file = Column(UnicodeText, nullable=False)
    number = Column(Integer, nullable=False)
    modified = Column(Integer, nullable=False)

    def __str__(self):
        return '%s: %s (%s)' % (self.artist.name, self.name, self.album.name)
