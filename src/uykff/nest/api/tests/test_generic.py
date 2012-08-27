from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from time import time
from unittest import TestCase
from uykff.core.support.configure import Config

from uykff.nest.api.generic import GenericApi


class GenericTest(TestCase):

    def test_url(self):
        api = GenericApi('XYZ')
        url = api._build_url('artist', 'search', name='bob')
        assert url == 'http://developer.echonest.com/api/v4/artist/search?api_key=XYZ&name=bob', url


def make_handler():

    class Handler(BaseHTTPRequestHandler):

        count = 0

        def do_GET(self):
            self.send_response(200)
            self.__class__.count += 1
            self.send_header('X-RateLimit-Remaining', '%d' % (120-self.__class__.count))
            self.send_header('X-RateLimit-Used', '%d' % self.__class__.count)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'response')

    return Handler


class RateTest(TestCase):

    def test_rate(self):
        Config()
        address = ('localhost', 8765)
        server = HTTPServer(address, make_handler())
        try:
            Thread(target=lambda: server.serve_forever(0.001)).start()
            start = time()
            api = GenericApi('KEY', netloc='%s:%d' % address, burst=0)
            for i in range(10): api('foo', 'bar', a='b')
            duration = time() - start
            assert 4.9 <= duration < 5.1, duration
        finally:
            server.shutdown()

    def test_burst(self):
        Config()
        address = ('localhost', 8766)
        server = HTTPServer(address, make_handler())
        try:
            Thread(target=lambda: server.serve_forever(0.001)).start()
            start = time()
            api = GenericApi('KEY', netloc='%s:%d' % address)
            for i in range(10): api('foo', 'bar', a='b')
            duration = time() - start
            assert duration < 0.1, duration
        finally:
            server.shutdown()
