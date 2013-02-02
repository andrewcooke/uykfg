
from uykfg.core.tag import Tagger


class NestTagger(Tagger):

    TAGGER_NAME = 'nest'
    PRIORITY = 1

    def find_artist(self, session, id3):
        raise Exception('Unimplemented')
