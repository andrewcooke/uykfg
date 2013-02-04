
from hashlib import sha1
from logging import debug
from pickle import dumps, loads
from random import random
from time import time
from zlib import compress, decompress
from sqlalchemy import func

from sqlalchemy.orm.exc import NoResultFound

from uykfg.support.cache.db import CacheOwner, CacheData


MONTH = 3 * 24 * 60 * 60


class Cache:

    def __init__(self, function, Session, name=None, max_lifetime=None, max_size=None):
        self._function = function
        self._session = Session()
        if not name: name = function.__name__
        try:
            owner = self._session.query(CacheOwner).filter(CacheOwner.name == name).one()
            if max_lifetime: owner.max_lifetime = max_lifetime
            if max_size: owner.max_size = max_size
        except NoResultFound:
            owner = CacheOwner(name=name,
                max_lifetime=max_lifetime if max_lifetime else MONTH,
                max_size=max_size if max_size else 1e9)
            self._session.add(owner)
        self._owner = owner
        self.hits= 0
        self.misses = 0

    def __call__(self, *args, **kargs):
        self._expire()
        key = self._encode_key(*args, **kargs)
        cached_value = self._session.query(CacheData).\
            filter(CacheData.owner == self._owner, CacheData.key == key).first()
        if cached_value:
            debug('cache hit for %s' % repr((args, kargs)))
            value = self._decode_value(cached_value.value)
            cached_value.used = time()
            self.hits += 1
        else:
            debug('cache miss for %s' % repr((args, kargs)))
            value = self._function(*args, **kargs)
            encoded_value = self._encode_value(value)
            size = len(key) + len(encoded_value)
            self._session.add(CacheData(owner=self._owner, key=key,
                value=encoded_value, size=size,
                expires=int(time() + self._owner.max_lifetime * (0.5 + random()))))
            self.misses += 1
            self._owner.total_size += size
            self._reduce()
        self._session.commit()
        return value

    def _encode_key(self, *args, **kargs):
        hash = sha1()
        for arg in args: hash.update(('%r' % arg).encode('utf8'))
        for key in sorted(kargs):
            hash.update(('%r:%r' % (key, kargs[key])).encode('utf8'))
        return hash.hexdigest()

    def _encode_value(self, value):
        return compress(dumps(value))

    def _decode_value(self, value):
        return loads(decompress(value))

    def _expire(self):
        query = self._session.query(CacheData)\
            .filter(CacheData.expires < time(), CacheData.owner == self._owner)
        count = query.count()
        if count:
            debug('deleting %d cache entries' % count)
            query.delete()
            size = self._session.query(func.sum(CacheData.size))\
                .filter(CacheData.owner == self._owner).scalar()
            if not size: size = 0
            self._owner.total_size = size

    def _reduce(self):
        while self._owner.total_size > self._owner.max_size:
            expired = self._session.query(CacheData)\
                .filter(CacheData.owner == self._owner)\
                .order_by(CacheData.used.asc()).first()
            debug('deleting expired value last used at %s (%d)' % (expired.used, expired.size))
            self._owner.total_size -= expired.size
            self._session.delete(expired)
            self._session.commit()
