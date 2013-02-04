
from time import time
from sqlalchemy.orm import relationship

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Binary, Text

from uykfg.support.db import TableBase



class CacheOwner(TableBase):

    __tablename__ = 'cache_owner'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    total_size = Column(Integer, nullable=False, default=0)
    max_size = Column(Integer, nullable=False)
    max_lifetime = Column(Integer, nullable=False)


class CacheData(TableBase):

    __tablename__ = 'cache_data'
    owner_id = Column(Integer, ForeignKey(CacheOwner.id), primary_key=True, nullable=False)
    owner = relationship(CacheOwner, backref='data')
    key = Column(Text, primary_key=True, nullable=False)
    value = Column(Binary, nullable=False)
    size = Column(Integer, nullable=False)
    # times stored to nearest second
    expires = Column(Integer, nullable=False)
    used = Column(Integer, nullable=False, default=time)
