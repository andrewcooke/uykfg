
'''
We assume that every album is in a separate directory, and that the
tracks are files within that directory.  Tracks have a single artist
(which may be a list of names etc).  We don't try to unify individuals
(artists are "groups", not "performers").

Different artists can have the same name,  We include a disambiguation
field that can be used by the appropriate metadata service.
'''

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.expression import func, select
from sqlalchemy.types import Integer, UnicodeText, DateTime

from uykff.core.db.support import Base


ALBUMS, TRACKS = 'albums', 'tracks'


class __Common(Base):

    __abstract__ = True
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)

    @classmethod
    def count(cls, session):
        return session.connection().execute(select([func.count(cls.id)])).scalar()


class Artist(__Common):

    __tablename__ = 'artists'
    disambiguation = Column(UnicodeText, default='')

    def __str__(self):
        return '%s (%s' % (self.name, self.disambiguation)


class Album(__Common):

    __tablename__ = ALBUMS
    path = Column(UnicodeText)

    def __str__(self):
        return '%s (%s)' % (self.name, self.path)


class Track(__Common):

    __tablename__ = TRACKS
    artist_id = Column(Integer, ForeignKey(Artist.id))
    artist = relationship(Artist, backref=TRACKS)
    album_id = Column(Integer, ForeignKey(Album.id))
    album = relationship(Album, backref=TRACKS)
    file = Column(UnicodeText)
    number = Column(Integer)
    modified = Column(DateTime)

    def __str__(self):
        return '%s: %s (%s)' % (self.artist.name, self.name, self.album.name)
