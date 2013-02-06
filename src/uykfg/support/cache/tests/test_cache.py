
from time import sleep
from unittest import TestCase

from uykfg.music.db import startup
from uykfg.support.configure import Config
from uykfg.support.cache import Cache


def stringify(*args, **kargs):
    return '%r %r' % (args, kargs)


class CacheTest(TestCase):

    def _assert(self, result, target):
        assert result == target, result

    def test_cache(self):
        config = Config(db_url='sqlite://')
        session = startup(config)
        cached_stringify = Cache(stringify, session)
        self._assert(stringify(1, 2, three=4), "(1, 2) {'three': 4}")
        self._assert(cached_stringify(1, 2, three=4), "(1, 2) {'three': 4}")
        assert cached_stringify.hits == 0, cached_stringify.hits
        assert cached_stringify.misses == 1, cached_stringify.misses
        self._assert(cached_stringify(1, 2, three=4), "(1, 2) {'three': 4}")
        assert cached_stringify.hits == 1, cached_stringify.hits
        assert cached_stringify.misses == 1, cached_stringify.misses

        self._assert(cached_stringify(1, 2, three=5), "(1, 2) {'three': 5}")
        assert cached_stringify.misses == 2, cached_stringify.misses

        assert cached_stringify._owner.total_size == 154, cached_stringify._owner.total_size
        cached_stringify = Cache(stringify, session, max_size=77, value_lifetime=1)
        self._assert(cached_stringify(1, 2, three=6), "(1, 2) {'three': 6}")
        assert cached_stringify.misses == 1, cached_stringify.misses
        assert cached_stringify._owner.total_size == 77, cached_stringify._owner.total_size
        sleep(3)
        self._assert(cached_stringify(1, 2, three=7), "(1, 2) {'three': 7}")
        assert cached_stringify.misses == 2, cached_stringify.misses
        assert cached_stringify._owner.total_size == 77, cached_stringify._owner.total_size
