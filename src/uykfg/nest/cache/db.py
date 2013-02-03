
from time import time

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Binary, Text

from uykfg.music.db.support import TableBase


class NestCache(TableBase):

    __tablename__ = 'nest_cache'
    key = Column(Text, primary_key=True)
    value = Column(Binary, nullable=False)
    size = Column(Integer, nullable=False)
    # times stored to nearest second
    added = Column(Integer, nullable=False, default=time)
    used = Column(Integer, nullable=False, default=time)

