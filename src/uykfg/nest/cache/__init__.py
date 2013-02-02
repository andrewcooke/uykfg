
from hashlib import sha1
from datetime import datetime
from logging import debug
from pickle import dumps, loads
from threading import Thread
from time import time, sleep
from zlib import compress, decompress

from sqlalchemy.sql.expression import func

from uykfg.nest.cache.db import NestCache


class Cache:

    def __init__(self, function, Session,
                 period=3600, max_lifetime=None, max_size=1e9, clean=True):
        self._function = function
        self._session = Session()
        if clean and not __CACHE_CLEANER:
            __CACHE_CLEANER = CacheCleaner(Session, period, max_lifetime, max_size)
        self.hits= 0
        self.misses = 0

    def __call__(self, *args, **kargs):
        key = self._encode_key(*args, **kargs)
        cached_value = self._session.query(NestCache).filter(NestCache.key == key).first()
        if cached_value:
            debug('cache hit for %s' % repr((args, kargs)))
            value = self._decode_value(cached_value.value)
            cached_value.used = datetime.today()
            self.hits += 1
        else:
            debug('cache miss for %s' % repr((args, kargs)))
            value = self._function(*args, **kargs)
            encoded_value = self._encode_value(value)
            self._session.add(NestCache(key=key, value=encoded_value,
                size=len(key) + len(encoded_value)))
            self.misses += 1
        self._session.commit()
        return value

    def _encode_key(self, *args, **kargs):
        hash = sha1()
        for arg in args: hash.update(('%r' % arg).encode('utf8'))
        for key in sorted(kargs):
            hash.update(('%r:%r' % (key, kargs[key])).encode('utf8'))
        return hash.digest()

    def _encode_value(self, value):
        return compress(dumps(value))

    def _decode_value(self, value):
        return loads(decompress(value))


__CACHE_CLEANER = None
'''Singleton used to clean the cache.'''

class CacheCleaner:

    def __init__(self, Session, period=3600, max_lifetime=None, max_size=1e9,
                 standalone=True):
        self._session = Session()
        self._period = period
        self._max_lifetime = max_lifetime
        self._max_size = max_size
        if standalone:
            self._running = True
            Thread(target=self).start()

    def __call__(self):
        while self._running:
            start = time()
            self._clean_expired()
            self._clean_least_used()
            sleep(max(0, start + self._period - time()))

    def _clean_expired(self):
        count = 0
        if self._max_lifetime:
            cutoff = datetime.fromtimestamp(time() - self._max_lifetime)
            query = self._session.query(NestCache).filter(NestCache.added < cutoff)
            count = query.count()
            debug('deleting %d cache entries' % count)
            query.delete()
            self._session.commit()
        return count

    def _over_size(self):
        size = self._session.query(func.sum(NestCache.size)).scalar()
        return size and size > self._max_size

    def _clean_least_used(self):
        count = 0
        while self._over_size():
            expired = self._session.query(NestCache).order_by(NestCache.used.desc()).first()
            debug('deleting expired value last used at %s' % expired.used)
            self._session.delete(expired)
            self._session.commit()
            count += 1
        return count


