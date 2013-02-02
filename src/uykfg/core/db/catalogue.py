
'''
We assume that every album is in a separate directory, and that the
tracks are files within that directory.  Tracks have a single artist
(which may be a list of names etc).  We don't try to unify individuals
(artists are "groups", not "performers").

Different artists can have the same name,  We include a disambiguation
field that can be used by the appropriate metadata service.
'''

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Index
from sqlalchemy.sql.expression import func, select
from sqlalchemy.types import Integer, UnicodeText, DateTime, Unicode

from uykfg.core.db.support import TableBase


class __Common(TableBase):

    __abstract__ = True
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)

    @classmethod
    def count(cls, session):
        return session.connection().execute(select([func.count(cls.id)])).scalar()


class Artist(__Common):

    __tablename__ = 'core_artists'
    tagger_name = Column(Unicode, nullable=False)
    tag_id = Column(Integer, nullable=False)
    Index('artist_tag_idx', 'Artist.tagger_name', 'Artist.tag_id')

    def __str__(self):
        return '%s (%d:%d)' % (self.name, self.tagger_id, self.tag_id)


class Album(__Common):

    __tablename__ = 'core_albums'
    path = Column(UnicodeText)

    def __str__(self):
        return '%s (%s)' % (self.name, self.path)


class Track(__Common):

    __tablename__ = 'core_tracks'
    artist_id = Column(Integer, ForeignKey(Artist.id), nullable=False)
    artist = relationship(Artist, backref='tracks')
    album_id = Column(Integer, ForeignKey(Album.id), nullable=False)
    album = relationship(Album, backref='tracks')
    file = Column(UnicodeText, nullable=False)
    number = Column(Integer, nullable=False)
    modified = Column(DateTime, nullable=False)

    def __str__(self):
        return '%s: %s (%s)' % (self.artist.name, self.name, self.album.name)
