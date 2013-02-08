
from logging import debug, warning
from urllib.error import URLError
from collections import Counter
from sqlalchemy.orm.exc import NoResultFound

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist
from uykfg.nest.api import RateLimitingApi
from uykfg.nest.db import NestArtist
from uykfg.support.cache import Cache
from uykfg.support.configure import Config
from uykfg.support.sequences import unpack


def single_artist(artists):
    known = set()
    for (id, name) in artists:
        if id not in known:
            yield id, name
            known.add(id)


class FinderError(Exception): pass


class Finder:

    def __init__(self, config, session):
        self._api = Cache(RateLimitingApi(config.api_key), session)

    def find_track_artist(self, session, artist, title):
        try:
            return self._artist(session, artist, *next(self._song_search(title, artist=artist)))
        except (StopIteration, URLError):
            raise FinderError(artist)

    def _song_search(self, title, artist=None, results=1):
        params = {'title': title, 'results': results, 'sort': 'artist_familiarity-desc'}
        if artist: params['artist'] = artist
        for song in unpack(self._api('song', 'search', **params), 'response', 'songs'):
            yield song['artist_id'], song['artist_name']

    def _artist(self, session, id3_name, nest_id, nest_name):
        try:
            nest_artist = session.query(NestArtist).filter(NestArtist.id == nest_id).one()
        except NoResultFound:
            debug('creating nest artist %s:%s' % (nest_name, nest_id))
            nest_artist = NestArtist(id=nest_id, name=nest_name)
            session.add(nest_artist)
            session.commit()
        for artist in nest_artist.artists:
            if artist.name == id3_name: return artist
        debug('creating artist %s' % id3_name)
        artist = Artist(name = id3_name)
        session.add(artist)
        nest_artist.artists.append(artist)
        session.commit()
        return artist

    def find_tracks_artist(self, session, artist, titles):
        artists = Counter()
        for title in titles:
            try:
                artists.update(single_artist(self._song_search(title, results=15)))
                debug(artists)
            except URLError as e: debug(e)
        if artists:
            (id, name), score = artists.most_common(1)[0]
            if score > 2:
                debug('voted for %s:%s (%d)' % (name, id, score))
                return self._artist(session, artist, id, name)
            else:
                debug('inconclusive vote (%s: %d)' % (name, score))
        raise FinderError(', '.join(titles))

    def find_artist(self, session, artist):
        try: return self._artist(session, artist, *self._artist_search(artist))
        except (IndexError, AttributeError, URLError): raise FinderError(artist)

    def _artist_search(self, artist):
        artist = unpack(self._api('artist', 'search', name=artist,
                    results=1, sort='familiarity-desc'),
            'response', 'artists', 0)
        return artist['id'], artist['name']

    def delete_artist(self, session, artist):
        try:
            nest_artist = session.query(NestArtist)\
                .filter(NestArtist.artists.any(id=artist.id)).one()
            nest_artist.artists.remove(artist)
        except NoResultFound:
            warning('no nest artist for %s' % artist.name)



if __name__ == '__main__':
    config = Config.default()
    session = startup(config)
    finder = Finder(config, session)
    class Object: pass
    id3 = Object()
    id3.artist = 'Miles'
    id3.title = 'Blue'
    print(finder.find_artist(session, id3))
