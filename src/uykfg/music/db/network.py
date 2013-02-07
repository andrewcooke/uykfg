
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from uykfg.music.db.catalogue import Artist
from uykfg.support.db import TableBase


class Link(TableBase):

    __tablename__ = 'music_links'
    src_id = Column(Integer, ForeignKey(Artist.id), primary_key=True, nullable=False)
    src = relationship(Artist, backref='srcs', primaryjoin=src_id==Artist.id)
    dst_id = Column(Integer, ForeignKey(Artist.id), primary_key=True, nullable=False)
    dst = relationship(Artist, backref='dsts', primaryjoin=dst_id==Artist.id)
