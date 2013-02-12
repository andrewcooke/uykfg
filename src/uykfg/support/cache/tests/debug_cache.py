
from uykfg.music.db import startup
from uykfg.support.cache import CacheData, decode_value
from uykfg.support.configure import Config


def debug():
    config = Config(db_url='sqlite:////home/andrew/.uykfgdb')
    session = startup(config)
    for data in session.query(CacheData).filter(CacheData.exception == True).all():
        print('key %r' % data.key)
        print('value %r' % decode_value(data.value))
    session.query(CacheData).filter(CacheData.exception == True).delete()


if __name__ == '__main__':
    debug()
