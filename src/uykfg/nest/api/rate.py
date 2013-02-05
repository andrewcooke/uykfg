
from logging import debug, warning
from time import time, sleep
from urllib.parse import urlencode, quote, urlunparse
from urllib.request import urlopen


class RateEstimator:
    '''
    Manage a queue of timestamps made over `period` seconds.
    '''

    def __init__(self, period=60, bias=0.1):
        self._period = period
        self._bias = bias
        self._queue = []
        self._previous_time = None
        self._previous_used = None

    def update(self, used):
        '''
        Call when a new request is made.  The local rate is biased slightly
        to place downwards pressure on the greediest clients.
        '''
        now = time()
        local_count, local_rate, interval = self._local(now)
        external_rate = self._external(now, used, local_count)
        return now, local_rate * (1 + self._bias), interval, external_rate

    def _external(self, now, used, local_count):
        '''
        Take the larger of two estimates of the external rate.  One from the
        total number used in the last minute (corrected for the number of
        local requests); the other from the change in the number used since
        the last request.
        '''
        if self._previous_time:
            rate = self._period * (used - self._previous_used - 1) / (now - self._previous_time)
            rate = max(rate, used - local_count)
        else:
            rate = used - local_count
        self._previous_time = now
        self._previous_used = used
        return rate

    def _local(self, now):
        '''
        Take the larger of two estimates for the local rate.  One from the
        queue size (number of requests in last minute); the other from the
        time gap between the last two connections.
        '''
        self._queue.append(now)
        while self._queue[0] < now - self._period: self._queue.pop(0)
        count = len(self._queue)
        if count > 1:
            rate = self._period * (count - 1) / (now - self._queue[0])
            interval = self._queue[-1] - self._queue[-2]
            rate = max(rate, self._period / interval)
        else:
            rate, interval = 0, 0
        return count, rate, interval


class RateLimitingApi:
    '''
    Make a REST call to the Echo Nest API, via a very general interface.

    The rate of requests is managed to avoid exceeding the Echo Nest
    restrictions.
    '''

    def __init__(self, api_key, scheme='http', netloc='developer.echonest.com',
                 prefix=['api', 'v4'],
                 period=60, rate_limit=120, target=(0.8, 0.9), slower=1.1, faster=0.9):

        self._api_key = api_key
        self._scheme = scheme
        self._netloc = netloc
        self._prefix = prefix

        self._period = float(period)
        self._rate_limit = rate_limit
        self._target = target # target rate is `target * rate_limit`
        self._slower = slower # the scaling factor for increasing pause
        self._faster = faster # the scaling factor for decreasing pause

        self._estimator = RateEstimator(period)
        self._no_call_before = 0
        self._used = 0

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

    def _limit_rate(self):
        '''
        Respect any pre-calculated rate limit.
        '''
        now = time()
        if now < self._no_call_before:
            delta = self._no_call_before - now
            debug('sleeping for %fs' % delta)
            sleep(delta)

    def _do_request(self, url):
        '''
        Make the request and pull rate information from the response headers.
        '''
        with urlopen(url) as input:
            self._rate_limit = int(input.info()['X-RateLimit-Limit'])
            self._used = int(input.info()['X-RateLimit-Used'])
            debug('rate limit: %d; used: %d' % (self._rate_limit, self._used))
            return input.read()

    def _update_rate_estimate(self):
        '''
        Combine the local and external rates to estimate the (upper limit) on
        the global rate.  Then "blindly" adjust our rate depending on whether
        the total rate is above or below the target band.
        '''
        now, local_rate, interval, external_rate = self._estimator.update(self._used)
        if self._used >= self._rate_limit:
            warning('hit global hard limit; back-off and restart')
            self._no_call_before = now + self._period
        elif interval:
            total_rate = local_rate + external_rate
            debug('rates (per %ds)  local: %.1f; external: %.1f; total: %.1f; target: %.1f-%.1f' %
                (self._period, local_rate, external_rate, total_rate,
                 self._target[0] * self._rate_limit, self._target[1] * self._rate_limit))
            if total_rate > self._target[1] * self._rate_limit:
                interval *= self._slower
            elif total_rate < self._target[0] * self._rate_limit:
                interval *= self._faster
            interval = min(self._period / 2, max(self._period / self._rate_limit, interval))
            self._no_call_before = now + interval
        else:
            debug('too little information to estimate rates')
            self._no_call_before = now + (self._period / self._rate_limit)

    def __call__(self, api, method, **kargs):
        '''
        Make an API call.  The URL is generated according to the parameters
        and `__init__()` values.  Calls may be delayed to limit request rates.
        The response is returned as text.
        '''
        url = self._build_url(api, method, **kargs)
        self._limit_rate()
        try:
            return self._do_request(url)
        finally:
            self._update_rate_estimate()
