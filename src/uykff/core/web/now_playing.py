
from cherrypy import expose

@expose()
def now_playing():
    return 'now playing'

