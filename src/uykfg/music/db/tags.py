
from sqlalchemy import Table, Column, Integer, ForeignKey, UnicodeText
from sqlalchemy.orm import relationship
from uykfg.music.db.catalogue import Artist
from uykfg.support.db import TableBase


artists_to_tags = Table('music_artists_and_music_tags', TableBase.metadata,
    Column('artist_id', Integer, ForeignKey('music_artists.id'), nullable=False),
    Column('tag_id', Integer, ForeignKey('music_tags.id'), nullable=False)
)


class Tag(TableBase):

    __tablename__ = 'music_tags'
    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(UnicodeText, nullable=False, index=True, unique=True)
    artists = relationship(Artist, secondary=artists_to_tags)

