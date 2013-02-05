
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Integer, Unicode, UnicodeText

from uykfg.music.db.catalogue import Artist
from uykfg.support.db import TableBase


class NestArtist(TableBase):

    __tablename__ = 'nest_artists'
    id = Column(UnicodeText, primary_key=True, nullable=False) # echonest ID
    name = Column(UnicodeText, nullable=False)
    artist_id = Column(Integer, ForeignKey(Artist.id), nullable=True)
    artist = relationship(Artist)
