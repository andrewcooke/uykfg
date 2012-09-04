
from uykff.core.support.plugins import PluginMount


class Tagger(metaclass=PluginMount):
    '''
    Instances should contain:

    TAGGER_NAME: a unique name that identifies the tagger.  This should be
    short as it is stored in the database on each artist (eg: "nest").

    PRIORITY: taggers are ordered descending by (PRIORITY, TAGGER_NAME) (so
    a low numerical value for PRIORITY indicates that it should be preferred).

    find_artist(session, id3): return the tagger's artist class for the
    given track data.  This must have attributes `.id` and `.artist`.  The
    first is used to set `.tag_id` on the core Artist; the second is assigned
    to the id of the artist.  This approach is necessary to allow multiple
    tagger implementations.  The tagger's artist instance must be added to
    the session before it is returned.
    '''

    @classmethod
    def get_tagger(cls):
        candidates = [(t.PRIORITY, t.TAGGER_NAME, t) for t in cls.plugins]
        candidates.sort()
        if candidates: return candidates[0][2]()
        else: raise Exception('No tagger available')


