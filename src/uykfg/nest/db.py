
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Integer, Unicode

from uykfg.music.db.catalogue import Artist
from uykfg.support.db import TableBase


tags_and_artists = Table('nest_tags_and_artists', TableBase.metadata,
    Column('artist_id', Integer, ForeignKey('nest_artists.id')),
    Column('tag_id', Integer, ForeignKey('nest_tags.id'))
)


class NestArtist(TableBase):

    __tablename__ = 'nest_artists'
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey(Artist.id), nullable=True)
    artist = relationship(Artist)
    tags = relationship("tags", secondary=tags_and_artists, backref="artists")


class NestTag(TableBase):

    __tablename__ = 'nest_tags'
    id = Column(Integer, primary_key=True)
    tag = Column(Unicode, unique=True)
