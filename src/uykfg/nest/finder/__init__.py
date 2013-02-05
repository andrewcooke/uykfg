
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
    debug(json)
    for name in path: json = json[name]
    return json


class FinderError(Exception): pass


class Finder:

    def __init__(self, config, Session):
        self._api = Cache(RateLimitingApi(config.api_key), Session)

    def find_artist(self, session, id3):
        '''
        search for the track first, since that is more likely to disambiguate.
        '''
        try:
            return self._artist(session, id3.artist, *self._song_search(id3.artist, id3.title))
        except (AttributeError, IndexError) as e:
            debug(e)
            try:
                return self._artist(session, id3.artist, *self._artist_search(id3.artist))
            except (AttributeError, IndexError) as e:
                debug(e)
                raise FinderError(id3.artist)

    def _song_search(self, artist, title):
        song = unpack(self._api('song', 'search', artist=artist, title=title,
                results=1, sort='artist_familiarity-desc'),
            'response', 'songs', 0)
        return song['artist_id'], song['artist_name']

    def _artist_search(self, artist):
        artist = unpack(self._api('artist', 'search', name=artist,
                    results=1, sort='familiarity-desc'),
            'response', 'artists', 0)
        return artist['id'], artist['name']

    def _artist(self, session, id3_name, nest_id, nest_name):
        commit = False
        try:
            nest_artist = session.query(NestArtist).filter(NestArtist.id == nest_id).one()
        except NoResultFound:
            debug('creating nest artist %s:%s' % (nest_name, nest_id))
            nest_artist = NestArtist(id=nest_id, name=nest_name)
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
