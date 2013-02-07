
from http.server import HTTPServer, BaseHTTPRequestHandler
from logging import debug
from re import compile
from threading import Thread, Lock
from time import time, sleep
from unittest import TestCase

from uykfg.support.configure import Config
from uykfg.nest.api import RateLimitingApi


class UrlTest(TestCase):

    def test_url(self):
        api = RateLimitingApi('XYZ')
        url = api._build_url('artist', 'search', name='bob')
        assert url == 'http://developer.echonest.com/api/v4/artist/search?api_key=XYZ&name=bob', url


INDEX = compile(r'index=(\d+)')


def make_handler():

    class Handler(BaseHTTPRequestHandler):

        queue = []
        record = []
        lock = Lock()

        def do_GET(self):
            with self.__class__.lock:
                now = time()
                self.__class__.queue.append(now)
                while self.__class__.queue[0] < now - 60: self.__class__.queue.pop(0)
                count = len(self.__class__.queue)
                self.__class__.record.append((now, int(INDEX.search(self.path).groups()[0]), count))
            self.send_response(200)
            self.send_header('X-RateLimit-Remaining', '%d' % (120-count))
            self.send_header('X-RateLimit-Used', '%d' % count)
            self.send_header('X-RateLimit-Limit', '%d' % 120)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'response')

        @classmethod
        def dump(cls):
            for (time, index, count) in cls.record: print('%f %d %d' % (time, index, count))

    return Handler


class Client:

    def __init__(self, address, lock, counter, index):
        self._api = RateLimitingApi('KEY', netloc='%s:%d' % address)
        self._lock = lock
        self._counter = counter
        self._index = index
        self.count = 0

    def start(self):
        Thread(target=self).start()

    def __call__(self):
        while True:
            with self._lock:
                if self._counter[0]:
                    self._counter[0] -= 1
                    self.count += 1
                else:
                    break
            self._api('foo', 'bar', index=self._index)


class RateTest(TestCase):

    def test_single(self):
        Config()
        address = ('localhost', 8765)
        handler = make_handler()
        server = HTTPServer(address, handler)
        try:
            Thread(target=lambda: server.serve_forever(0.001)).start()
            start = time()
            api = RateLimitingApi('KEY', netloc='%s:%d' % address)
            for i in range(10): api('foo', 'bar', index=0)
            duration = time() - start
            handler.dump()
            assert 5 <= duration < 7, duration
        finally:
            server.shutdown()

    def do_multiple(self, address, n_clients, n_requests):
        Config()
        handler = make_handler()
        server = HTTPServer(address, handler)
        try:
            Thread(target=lambda: server.serve_forever(0.001)).start()
            lock = Lock()
            counter = [n_requests]
            clients = [Client(address, lock, counter, index) for index in range(n_clients)]
            start = time()
            for client in clients: client.start()
            while True:
                sleep(0.1)
                with lock:
                    if not counter[0]: break
            duration = time() - start
            handler.dump()
            expected = 60 * n_requests / (120.0 * 0.9)
            # check duration within 20% of expected
            assert expected * 0.8 < duration < expected * 1.2, (duration, expected)
            count = clients[0].count
            # check requests distributed fairly across clients
            for client in clients: assert count * 0.9 < client.count < count * 1.1, (client.count, count)
        finally:
            server.shutdown()

#    def test_pair(self):
#        self.do_multiple(('localhost', 8766), 2, 500)

#    def test_many(self):
#        self.do_multiple(('localhost', 8767), 4, 2000)
