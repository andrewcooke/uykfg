
from logging import debug, warning, error
from urllib.error import URLError
from sqlalchemy.orm.exc import NoResultFound

from uykfg.music.db.catalogue import Artist
from uykfg.music.db.network import Link
from uykfg.nest.api import RateLimitingApi
from uykfg.nest.db import NestArtist
from uykfg.support.cache import Cache
from uykfg.support.sequences import unpack


EXCLUDE = {'Various', 'Various Artists'}

class Linker:

    def __init__(self, config, session):
        self._api = Cache(RateLimitingApi(config.api_key), session)
        self._max_links = config.max_links

    def link(self, session, src):
        try:
            links = 0
            id = session.query(NestArtist).join('artists').filter(Artist.id == src.id).one().id
            start, results, found = 0, 6, 0
            while links < self._max_links and results < 100:
                links = self._link_delta(session, src, start, results, links, id)
                start = results
                results *= 2
            if not links:
                warning('no links for %s' % src.name)
        except NoResultFound:
            warning('no nest artist for %s' % src.name)
        except (AttributeError, IndexError, URLError) as e:
            error(e)

    def _link_delta(self, session, src, start, results, links, id):
        commit = False
        try:
            for artist in unpack(self._api('artist', 'similar', id=id,
                                           start=start, results=results-start),
                                 'response', 'artists'):
                try:
                    nest_artist = session.query(NestArtist)\
                            .filter(NestArtist.id == artist['id']).one()
                    for dst in nest_artist.artists:
                        if links < self._max_links and dst.name not in EXCLUDE and \
                                not session.query(Link).filter(Link.src == src, Link.dst == dst).count():
                            debug('linking %s to %s' % (src.name, dst.name))
                            session.add(Link(src=src, dst=dst))
                            commit = True
                    links += 1 # count nest artists, not multiple local artists
                except NoResultFound:
                    pass
            if commit: session.commit()
            return links
        except ValueError as e:
            warning('%s, so deleting' % e)
            self._api.delete('artist', 'similar', id=id,
                             start=start, results=results-start)
            return 0

