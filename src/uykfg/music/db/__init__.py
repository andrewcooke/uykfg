
from logging import debug

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from uykfg.music.db.catalogue import TableBase


def startup(config):
    import uykfg.music.db.catalogue # force detection
    import uykfg.music.db.network # force detection
    import uykfg.music.db.tags # force detection
    metadata = TableBase.metadata
    debug('creating engine for %s' % config.db_url)
    engine = create_engine(config.db_url, echo=True)
    metadata.bind = engine
    debug('creating tables (if missing)')
    metadata.create_all()
    return sessionmaker(bind=engine)()


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
    return instance
