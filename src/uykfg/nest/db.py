
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, UnicodeText

from uykfg.music.db.catalogue import Artist
from uykfg.support.db import TableBase


artists_to_artists = Table('nest_artists_and_music_artists', TableBase.metadata,
    Column('nest_artist_id', UnicodeText, ForeignKey('nest_artists.id'), nullable=False),
    Column('music_artist_id', Integer, ForeignKey('music_artists.id'), nullable=False)
)


class NestArtist(TableBase):

    __tablename__ = 'nest_artists'
    id = Column(UnicodeText, primary_key=True, nullable=False) # echonest ID
    name = Column(UnicodeText, nullable=False)
    artists = relationship(Artist, secondary=artists_to_artists)
