
from sqlalchemy.schema import Column
from sqlalchemy.sql.expression import func
from sqlalchemy.types import Integer, DateTime, Binary, Text

from uykff.core.db.support import TableBase


class NestCache(TableBase):

    __tablename__ = 'nest_cache'
    key = Column(Text, primary_key=True)
    value = Column(Binary, nullable=False)
    size = Column(Integer, nullable=False)
    added = Column(DateTime, nullable=False, default=func.now())
    used = Column(DateTime, nullable=False, default=func.now())

