
from logging import debug
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from uykfg.music.db.catalogue import Artist
from uykfg.music.db.network import Link
from uykfg.nest.api import RateLimitingApi
from uykfg.nest.db import NestArtist
from uykfg.support.cache import Cache
from uykfg.support.sequences import unpack


class Linker:

    def __init__(self, config, session):
        self._api = Cache(RateLimitingApi(config.api_key), session)

    def link(self, session, src, target=8):
        try:
            id = session.query(NestArtist).join('artists').filter(Artist.id == src.id).one().id
            start, results, found = 0, 12, 0
            while found < target and results < 100:
                found += self._link_delta(session, src, start, results, target, id)
                start = results
                results *= 2
        except NoResultFound:
            debug('no nest artist for %s' % src.name)
        except (AttributeError, IndexError) as e:
            debug(e)

    def _link_delta(self, session, src, start, results, target, id):
        found = 0
        for artist in unpack(self._api('artist', 'similar', id=id,
                                       start=start, results=results-start),
                             'response', 'artists'):
            try:
                nest_artist = session.query(NestArtist)\
                        .filter(NestArtist.id == artist['id']).one()
                for dst in nest_artist.artists:
                    if found < target and\
                            not session.query(Link).filter(Link.src == src, Link.dst == dst).count():
                        debug('linking %s to %s' % (src.name, dst.name))
                        session.add(Link(src=src, dst=dst))
                        found += 1
            except NoResultFound:
                pass
        if found: session.commit()
        return found

