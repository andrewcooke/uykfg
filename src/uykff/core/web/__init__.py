
'''
The interface should have as few different URLs as possible.

The root should be an interesting mish-mash that shows what is playing
and allows exploration of related and new music.

In addition, components that need configuration will need to provide their
own pages.
'''

from logging import info

from cherrypy import server, engine, tree

from uykff.core.web.index import index
from uykff.core.web.view import Templates


Templates.register(__name__, __file__)


def startup(config):
    server.socket_host = config.web_address
    server.socket_port = config.web_port
    tree.mount(index)
    info('starting server on %s:%d' % (config.web_address, config.web_port))
    engine.start()
    engine.block()

