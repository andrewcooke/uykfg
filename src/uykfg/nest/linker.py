
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

    def link(self, session, src):
        try:
            commit = False
            id = session.query(NestArtist)\
                    .join('artists')\
                    .filter(Artist.id == src.id).one().id
            for artist in unpack(self._api('artist', 'similar', id=id), 'response', 'artists'):
                try:
                    nest_artist = session.query(NestArtist)\
                            .filter(NestArtist.id == artist['id']).one()
                    for dst in nest_artist.artists:
                        if not session.query(Link).filter(src=src, dst=dst).count():
                            debug('linking %s to %s' % (src.name, dst.name))
                            session.add(Link(src=src, dst=dst))
                            commit = True
                except NoResultFound:
                    pass
            if commit: session.commit()
        except NoResultFound:
            debug('no nest artist for %s' % src.name)
