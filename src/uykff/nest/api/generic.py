from logging import info, debug
from time import time, sleep
from urllib.parse import urlencode, quote, urlunparse
from urllib.request import urlopen


class GenericApi:

    def __init__(self, api_key, scheme='http', netloc='developer.echonest.com',
                 prefix=['api', 'v4'], buffer=5, burst=60, rate_limit=120):
        self._api_key = api_key
        self._scheme = scheme
        self._netloc = netloc
        self._prefix = prefix
        self._buffer = buffer
        self._rate_limit = rate_limit
        self._burst = burst
        self._remaining = rate_limit
        self._last_call = 0

    def _build_url(self, _api, _method, **kargs):
        path = '/'.join(map(quote, self._prefix + [_api, _method]))
        params = dict(kargs)
        params['api_key'] = self._api_key
        url = urlunparse((self._scheme, self._netloc, path, '', urlencode(params), ''))
        debug(url)
        return url

    def _limit_rate(self):
        '''
        We consume up to `burst` calls immediately.  After that, we pause so
        that remaining calls are spaced to fill the entire minute (with a
        slight safety margin given by `buffer`).  This is intended to give
        fast responses for small, infrequent requests while being fair when
        resources are limited.
        '''
        if self._remaining < self._rate_limit - self._burst:
            gap = 60.0 / (self._remaining - self._buffer)
            pause = max(0, (self._last_call + gap) - time())
            if pause:
                info('rate limiting: sleeping %fs' % pause)
                sleep(pause)

    def _do_request(self, url):
        try:
            with urlopen(url) as input:
                self._remaining = int(input.info()['X-RateLimit-Remaining'])
                debug('remaining: %d' % self._remaining)
                return input.read()
        finally:
            self._last_call = time()

    def __call__(self, _api, _method, **kargs):
        url = self._build_url(_api, _method, **kargs)
        self._limit_rate()
        return self._do_request(url)
