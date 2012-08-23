
from logging import debug

from sqlalchemy.engine import create_engine

from uykff.core.db.catalogue import Base


def startup(config):
    metadata = Base.metadata
    debug('creating engine for %s' % config.db_url)
    engine = create_engine(config.db_url)
    metadata.bind = engine
    debug('creating tables (if missing)')
    metadata.create_all()
    return engine


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
    return instance
