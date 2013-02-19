
from logging import debug, warning, error
from urllib.error import URLError, HTTPError
from collections import Counter
from re import compile

from sqlalchemy.orm.exc import NoResultFound

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist
from uykfg.music.db.tags import Tag
from uykfg.nest.api import RateLimitingApi
from uykfg.nest.db import NestArtist
from uykfg.support import twice_monthly
from uykfg.support.cache import Cache
from uykfg.support.configure import Config
from uykfg.support.sequences import unpack, lmap


def distinct_artists(artists):
    known = set()
    for (id, name) in artists:
        if id not in known:
            yield id, name
            known.add(id)


DROP_TRAILING_PARENS = compile(r'(.{6,}?)\s*\([^)]+\)\s*$')
UNWRAP = compile(r'(?:\s*[Tt]he\s+)?(.+)\s+(?:[Oo]rchestra|[Bb]and)[\s|$]')
SPLIT = compile(r'(.+?)(?:&|,|\+|/|[,\s]+(?:[Aa][Nn][Dd]|[Yy]|[Ii]|[Vv][Ss]|[Ff][Tt].?|[Ff][Ee][Aa][Tt].?|[Ff]eaturing|-|[Ww]ith|[Aa][Kk][Aa])\s+)(.+)')

def alternatives(artist, known, original):
    name = artist.strip()
    if name not in known:
        known.add(name)
        if original.strip() != name: debug('%s -> %s' % (original, name))
        yield name
    for expr in (DROP_TRAILING_PARENS, UNWRAP):
        match = expr.match(artist)
        if match:
            for name in possible_names(match.group(1), first=True, known=known, original=original):
                yield name

def possible_names(artist, first=True, known=None, original=None):
    if not known: known = set()
    if not original: original = artist
    match = SPLIT.match(artist)
    if first or not match:
        for name in alternatives(artist, known, original): yield name
    if match:
        for name in alternatives(match.group(1), known, original): yield name
        for name in possible_names(match.group(2), first=False, known=known, original=original): yield name


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
                debug('no nest artist for %s' % track.artist.name)
                return True
        return False

    def find_track_artist(self, session, artist, title):
        for name in possible_names(artist):
            try:
                return self._create_artist(session, artist,
                    *next(self._song_search(title, artist=name)))
            except StopIteration: pass
            except URLError as e: error('find_track_artist: %s' % e)
        raise FinderError(artist)

    def _create_artist(self, session, id3_name, nest_id, nest_name):
        nest_artist = self._nest_artist(session, nest_id, nest_name)
        for artist in nest_artist.artists:
            if artist.name == id3_name:
                if not artist.tags or twice_monthly():
                    self._reset_tags(session, nest_artist, artist)
                return artist
        return self._music_artist(session, nest_artist, id3_name)

    def _nest_artist(self, session, nest_id, nest_name):
        try:
            nest_artist = session.query(NestArtist).filter(NestArtist.id == nest_id).one()
        except NoResultFound:
            debug('creating nest artist %s:%s' % (nest_name, nest_id))
            nest_artist = NestArtist(id=nest_id, name=nest_name)
            session.add(nest_artist)
        return nest_artist

    def _music_artist(self, session, nest_artist, id3_name):
        debug('creating artist %s' % id3_name)
        artist = Artist(name = id3_name)
        session.add(artist)
        self._append_tags(session, nest_artist, artist)
        nest_artist.artists.append(artist)
        return artist

    def _tags(self, session, nest_artist):
        for result in unpack(
                self._api('artist', 'terms', id=nest_artist.id, sort='weight'),
                'response', 'terms'):
            text = result['name']
            try:
                tag = session.query(Tag).filter(Tag.text == text).one()
            except NoResultFound:
                tag = Tag(text=text)
                session.add(tag)
            yield tag

    def _append_tags(self, session, nest_artist, artist):
        for tag in self._tags(session, nest_artist): artist.tags.append(tag)
        debug('tags for %s: %s' % (artist.name, ', '.join(tag.text for tag in artist.tags)))

    def _reset_tags(self, session, nest_artist, artist):
        debug('reset tags for %s' % artist.name)
        for tag in artist.tags: artist.tags.remove(tag)
        self._append_tags(session, nest_artist, artist)

    def _song_search(self, title, artist=None, results=1):
        params = {'title': title, 'results': results, 'sort': 'artist_familiarity-desc'}
        if artist: params['artist'] = artist
        for song in unpack(self._api('song', 'search', **params), 'response', 'songs'):
            yield song['artist_id'], song['artist_name']
        match = DROP_TRAILING_PARENS.match(title)
        if match:
            title = match.group(1)
            debug(' retrying with %s' % title)
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
                return self._create_artist(session, artist, id, name)
            else:
                debug('inconclusive vote (%s: %d)' % (name, score))
        raise FinderError(', '.join(titles))

    def find_artist(self, session, artist):
        try: return self._create_artist(session, artist, *self._artist_search(artist))
        except URLError as e: error('find_artist: %s' % e)
        except (IndexError, AttributeError): pass
        raise FinderError(artist)

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
