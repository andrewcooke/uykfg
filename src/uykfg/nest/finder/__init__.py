
from logging import debug
from json import loads
from sqlalchemy.orm.exc import NoResultFound

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist
from uykfg.nest.api.rate import RateLimitingApi
from uykfg.nest.db import NestArtist
from uykfg.support.cache import Cache
from uykfg.support.configure import Config


def unpack(json, *path):
    json = loads(json.decode('utf8'))
    for name in path: json = json[name]
    return json


class Finder:

    def __init__(self, config, Session):
        self._api = Cache(RateLimitingApi(config.api_key), Session)

    def find_artist(self, session, id3):
        '''
        search for the track first, since that is more likely to disambiguate.
        '''
        return self._artist(session, id3.artist,
            *self._song_search(id3.artist, id3.title))

    def _song_search(self, artist, title):
        json = self._api('song', 'search', artist=artist, title=title,
            results=1, sort='artist_familiarity-desc')
        song = unpack(json, 'response', 'songs', 0)
        return song['artist_id'], song['artist_name']

    def _artist(self, session, id3_name, id, name):
        commit = False
        try:
            nest_artist = session.query(NestArtist).filter(NestArtist.id == id).one()
        except NoResultFound:
            debug('creating nest artist %s:%s' % (name, id))
            nest_artist = NestArtist(id=id, name=name)
            session.add(nest_artist)
            commit = True
        if not nest_artist.artist:
            debug('creating artist %s' % id3_name)
            artist = Artist(name = id3_name)
            session.add(artist)
            nest_artist.artist = artist
            commit = True
        if commit: session.commit()
        return nest_artist.artist


if __name__ == '__main__':
    config = Config.default()
    Session = startup(config)
    finder = Finder(config, Session)
    class Object: pass
    id3 = Object()
    id3.artist = 'Miles'
    id3.title = 'Blue'
    print(finder.find_artist(Session(), id3))
