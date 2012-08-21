
from logging import info

from cherrypy import server, engine, tree

from uykff.core.web.catalogue_mgmt import catalogue_mgmt
from uykff.core.web.now_playing import now_playing


def startup(config):
    server.socket_host = config.web_address
    server.socket_port = config.web_port
    tree.mount(now_playing)
    tree.mount(catalogue_mgmt, '/catalogue')
    info('starting server on %s:%d' % (config.web_address, config.web_port))
    engine.start()
    engine.block()

