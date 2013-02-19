
from logging import debug, warning, error
from sys import stderr
from time import time, sleep
from urllib.error import HTTPError
from urllib.parse import urlencode, quote, urlunparse
from urllib.request import urlopen
from uykfg.support.cache import Fallback


class RateLimitingApi:
    '''
    Make a REST call to the Echo Nest API, via a very general interface.

    The rate of requests is managed to avoid exceeding the Echo Nest
    restrictions.
    '''

    def __init__(self, api_key, scheme='http', netloc='developer.echonest.com',
                 prefix=['api', 'v4'], greedy=1.3):

        self._api_key = api_key
        self._scheme = scheme
        self._netloc = netloc
        self._prefix = prefix
        self._greedy = greedy
        self._until = time()

    def _build_url(self, _api, _method, **kargs):
        '''
        Construct a URL for the Echo Nest REST API.  `_api` is something like
        "song" or "artist"; `_method` might be "search"; other keyword
        arguments are sent as query parameters.
        '''
        path = '/'.join(map(quote, self._prefix + [_api, _method]))
        params = dict(kargs)
        params['api_key'] = self._api_key
        url = urlunparse((self._scheme, self._netloc, path, '', urlencode(params), ''))
        debug(url)
        return url

    def _wait_until(self):
        while True:
            delta = self._until - time()
            if delta <= 0: return
            debug('sleeping for %fs' % delta)
            sleep(delta)

    def _do_request(self, url):
        '''
        Make the request and pull rate information from the response headers.
        '''
        with urlopen(url) as input:
            rate_limit = int(input.info()['X-RateLimit-Limit'])
            used = int(input.info()['X-RateLimit-Used'])
            delta = 60 / max(1, (rate_limit - used))**self._greedy
            debug('limit: %d; count: %d; delay: %fs' % (rate_limit, used, delta))
            self._until = time() + delta
            return input.read()

    def __call__(self, api, method, **kargs):
        '''
        Make an API call.  The URL is generated according to the parameters
        and `__init__()` values.  Calls may be delayed to limit request rates.
        The response is returned as text.
        '''
        url = self._build_url(api, method, **kargs)
        self._wait_until()
        retry = 2
        try:
            while retry:
                try:
                    return self._do_request(url)
                except HTTPError as e:
                    error(e)
                    if retry:
                        debug('retrying in 60s')
                        retry -= 1
                        sleep(60)
                    else:
                        raise e
        except Exception as e:
            raise Fallback(e)
