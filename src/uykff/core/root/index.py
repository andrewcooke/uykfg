
from cherrypy import tools

from uykff.core.support.io import parent
from uykff.core.web.mustache import mustache


@tools.staticdir(dir='static', root=parent(__file__))
@mustache(__name__)
def index():
    return {}

