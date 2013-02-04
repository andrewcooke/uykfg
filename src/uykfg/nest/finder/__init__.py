
from uykfg.nest.api.rate import RateLimitingApi


class Finder:

    def __init__(self, config):
        self.api = RateLimitingApi(api_key)

    def find_artist(self, session, id3):
        pass