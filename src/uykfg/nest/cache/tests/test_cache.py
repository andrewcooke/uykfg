
from time import sleep
from unittest import TestCase

from uykfg.core.db import startup
from uykfg.core.support.configure import Config
from uykfg.nest.cache import Cache, CacheCleaner


def stringify(*args, **kargs):
    return '%r %r' % (args, kargs)


class CacheTest(TestCase):

    def _assert(self, result, target):
        assert result == target, result

    def test_cache(self):
        config = Config(db_url='sqlite://')
        Session = startup(config)
        cached_stringify = Cache(stringify, Session, clean=False)
        self._assert(stringify(1, 2, three=4), "(1, 2) {'three': 4}")
        self._assert(cached_stringify(1, 2, three=4), "(1, 2) {'three': 4}")
        assert cached_stringify.hits == 0, cached_stringify.hits
        assert cached_stringify.misses == 1, cached_stringify.misses
        self._assert(cached_stringify(1, 2, three=4), "(1, 2) {'three': 4}")
        assert cached_stringify.hits == 1, cached_stringify.hits
        assert cached_stringify.misses == 1, cached_stringify.misses

        assert CacheCleaner(Session, standalone=False)._clean_least_used() == 0
        self._assert(cached_stringify(1, 2, three=4), "(1, 2) {'three': 4}")
        assert cached_stringify.hits == 2, cached_stringify.hits
        assert cached_stringify.misses == 1, cached_stringify.misses
        assert CacheCleaner(Session, max_size=1, standalone=False)._clean_least_used() == 1
        self._assert(cached_stringify(1, 2, three=4), "(1, 2) {'three': 4}")
        assert cached_stringify.hits == 2, cached_stringify.hits
        assert cached_stringify.misses == 2, cached_stringify.misses

        assert CacheCleaner(Session, standalone=False)._clean_expired() == 0
        self._assert(cached_stringify(1, 2, three=4), "(1, 2) {'three': 4}")
        assert cached_stringify.hits == 3, cached_stringify.hits
        assert cached_stringify.misses == 2, cached_stringify.misses
        sleep(2)
        expired = CacheCleaner(Session, max_lifetime=1, standalone=False)._clean_expired()
        assert expired == 1, expired
        self._assert(cached_stringify(1, 2, three=4), "(1, 2) {'three': 4}")
        assert cached_stringify.hits == 3, cached_stringify.hits
        assert cached_stringify.misses == 3, cached_stringify.misses
