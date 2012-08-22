
from functools import wraps
from logging import debug, warning
from os import listdir
from os.path import dirname, join, splitext, abspath

from pystache import Renderer
from cherrypy import expose


class Templates:

    __registry = {}

    @classmethod
    def register(cls, module, path):
        '''
        Call from __init__.py when the module contains templates as:
          Templates.register(__name__, __file__)
        '''
        dir = dirname(abspath(path))
        cls.__registry[module] = dict((splitext(file)[0], join(dir, file))
                                      for file in listdir(dir)
                                      if file.endswith('.mustache'))

    def __init__(self):
        self.__cache = {}
        self.__renderer = Renderer(partials=self)

    def get(self, name):
        if name not in self.__cache:
            (module, file) = name.rsplit('.', 1)
            with open(self.__registry.get(module, {}).get(file)) as input:
               self.__cache[name] = input.read()
        return self.__cache.get(name)

    def render(self, name, model):
        return self.__renderer.render(self.get(name), model)


__CACHE = Templates()


def view(name, file=None):
    '''
    Call as either `@view('prefix.and.name')` or as `@view(__name__, 'file')`.
    '''
    if file: name += '.%s' % file
    def decorator(function):
        @expose
        @wraps(function)
        def wrapper(*args, **kargs):
            model = function(*args, **kargs)
            return __CACHE.render(name, model)
        return wrapper
    return decorator
