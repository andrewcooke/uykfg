
from cherrypy import tools

from uykff.core.support.io import parent
from uykff.core.web.mustache import view


STATIC = 'static'


@tools.staticdir(dir=STATIC, root=parent(__file__))
@view(__name__)
def index():
    return {}

