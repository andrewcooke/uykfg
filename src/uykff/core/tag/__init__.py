
from uykff.core.support.plugins import PluginMount


class Tagger(metaclass=PluginMount):
    '''
    Instances should contain:

    TAGGER_NAME: a unique name that identifies the tagger.  This should be
    short as it is stored in the database on each artist (eg: "nest").

    find_artist(id3, session): return the tagger's artist class for the
    given track data.  This must have attributes `.id` and `.artist`.  The
    first is used to set `.tag_id` on the core Artist; the second is assigned
    to the id of the artist.  This approach is necessary to allow multiple
    tagger implementations.  The tagger's artist instance must have already
    been added to the session.
    '''