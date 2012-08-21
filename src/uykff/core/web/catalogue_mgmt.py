
from cherrypy import expose


@expose()
def catalogue_mgmt():
    return 'catalogue mgmt'

