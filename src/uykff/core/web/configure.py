
from cherrypy import expose
from uykff.core.support.plugins import PluginMount


class ConfigurationController(PluginMount):
    '''
    Instances should provide the following attributes:
    url - a path relative to /configure (unique, so use specific names)
    link_text - the text that is included in a link
    description - a longer, HTML formatted description
    sort_key - a float used to sort entries

    Instances should be callable (they should be controllers).
    '''


def configure():
    return ConfigurationController.plugins

