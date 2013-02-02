
'''
http://martyalchin.com/2008/jan/10/simple-plugin-framework/
'''


class PluginMount(type):

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)
