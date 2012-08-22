
from functools import wraps
from os.path import join

from pystache import Renderer
from cherrypy import expose
from uykff.core.support.io import module_parent


class TemplateCache:

    def __init__(self):
        self.__cache = {}
        self.__renderer = Renderer(partials=self)

    def get(self, name):
        if name not in self.__cache:
            (module, file) = name.rsplit('.', 1)
            with open(join(module_parent(module), "%s.mustache" % file)) as input:
               self.__cache[name] = input.read()
        return self.__cache.get(name)

    def render(self, name, model):
        return self.__renderer.render(self.get(name), model)


__CACHE = TemplateCache()


def view(name, file=None):
    '''
    Call as either `@view(__name__)` or as `@view(__name__, 'alternate_file')`.
    '''
    if file: name += '%s.%s' % (name.rsplit('.')[0], name)
    def decorator(function):
        @expose
        @wraps(function)
        def wrapper(*args, **kargs):
            model = function(*args, **kargs)
            return __CACHE.render(name, model)
        return wrapper
    return decorator
