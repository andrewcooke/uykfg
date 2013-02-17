
from logging import debug, warning
from urllib.error import URLError
from collections import Counter
from re import compile

from sqlalchemy.orm.exc import NoResultFound

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist
from uykfg.nest.api import RateLimitingApi
from uykfg.nest.db import NestArtist
from uykfg.support.cache import Cache
from uykfg.support.configure import Config
from uykfg.support.sequences import unpack, lmap


def distinct_artists(artists):
    known = set()
    for (id, name) in artists:
        if id not in known:
            yield id, name
            known.add(id)


TEMPLATES = lmap(compile, [
    r'([^-&,+/]+?)\s*[-&,+/]',
    r'[^-&,+/]+[-&,+/]\s*([^-&,+/]+)',
    r'[^-&,+/]+[-&,+/][^-&,+/]+[-&,+/]\s*([^-&,+/]+)',
    r'[^-&,+/]+[-&,+/][^-&,+/]+[-&,+/][^-&,+/]+[-&,+/]\s*([^-&,+/]+)',
    r'[^-&,+/]+[-&,+/][^-&,+/]+[-&,+/][^-&,+/]+[-&,+/][^-&,+/]+[-&,+/]\s*([^-&,+/]+)',
    r'[^-&,+/]+[-&,+/][^-&,+/]+[-&,+/][^-&,+/]+[-&,+/][^-&,+/]+[-&,+/][^-&,+/]+[-&,+/]\s*([^-&,+/]+)',
    r'(.+?)\s+(?:[Aa][Nn][Dd]|[Yy]|[Ii]|[Vv][Ss]|[Ff][Tt].?|[Ff][Ee][Aa][Tt].?|[Ff]eaturing)\s+',
    r'.*\s+(?:[Aa][Nn][Dd]|[Yy]|[Ii]|[Vv][Ss]|[Ff][Tt].?|[Ff][Ee][Aa][Tt].?|[Ff]eaturing)\s+(.+)',
    r'(?:[Tt]he\s+)?(.+)\s+[Oo]rchestra',
    r'(?:[Tt]he\s+)?(.+)\s+[Bb]and',
])

def possible_names(artist):
    yield artist
    for template in TEMPLATES:
        match = template.match(artist)
        if match:
            result = match.group(1)
            debug('matched %s on %s to give %s' % (template.pattern, artist, result))
            yield result


DROP_TRAILING_PARENS = compile(r'(.{6,})\s*\([^)]+\)\s*$')


class FinderError(Exception): pass


class Finder:

    def __init__(self, config, session):
        self._api = Cache(RateLimitingApi(config.api_key), session)

    def missing_artist(self, session, tracks):
        tested = set()
        for track in tracks:
            try:
                if track.artist not in tested:
                    tested.add(track.artist)
                    self._nest_artist_from_music_artist(session, track.artist)
            except NoResultFound:
                warning('no nest artist for %s' % track.artist.name)
                return True
        return False

    def find_track_artist(self, session, artist, title):
        for name in possible_names(artist):
            try:
                return self._artist(session, artist, *next(self._song_search(title, artist=name)))
            except (StopIteration, URLError): pass
        raise FinderError(artist)

    def _artist(self, session, id3_name, nest_id, nest_name):
        try:
            nest_artist = session.query(NestArtist).filter(NestArtist.id == nest_id).one()
        except NoResultFound:
            debug('creating nest artist %s:%s' % (nest_name, nest_id))
            nest_artist = NestArtist(id=nest_id, name=nest_name)
            session.add(nest_artist)
        for artist in nest_artist.artists:
            if artist.name == id3_name: return artist
        debug('creating artist %s' % id3_name)
        artist = Artist(name = id3_name)
        session.add(artist)
        nest_artist.artists.append(artist)
        return artist

    def _song_search(self, title, artist=None, results=1):
        params = {'title': title, 'results': results, 'sort': 'artist_familiarity-desc'}
        if artist: params['artist'] = artist
        for song in unpack(self._api('song', 'search', **params), 'response', 'songs'):
            yield song['artist_id'], song['artist_name']
        match = DROP_TRAILING_PARENS.match(title)
        if match:
            title = match.group(1)
            debug('retrying with %s' % title)
            for id, name in self._song_search(title, artist, results):
                yield id, name

    def find_tracks_artist(self, session, artist, titles):
        artists = Counter()
        for title in titles:
            try:
                artists.update(distinct_artists(self._song_search(title, results=15)))
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

    def _nest_artist_from_music_artist(self, session, artist):
        return session.query(NestArtist)\
                .filter(NestArtist.artists.any(id=artist.id)).one()

    def delete_artist(self, session, artist):
        try:
            nest_artist = self._nest_artist_from_music_artist(session, artist)
            nest_artist.artists.remove(artist)
        except NoResultFound:
            debug('no nest artist for %s' % artist.name)



if __name__ == '__main__':
    config = Config.default()
    session = startup(config)
    finder = Finder(config, session)
    class Object: pass
    id3 = Object()
    id3.artist = 'Miles'
    id3.title = 'Blue'
    print(finder.find_artist(session, id3))
