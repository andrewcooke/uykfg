
from logging import debug
from sqlalchemy.sql.functions import random

from uykfg.music.db.catalogue import Artist
from uykfg.music.db.network import Link


def link_all(session, linker):
    for artist in session.query(Artist).order_by(random()).all():
        delete_src(session, artist)
        linker.link(session, artist)
    debug('done!')

def delete_src(session, artist):
    debug('deleting links from %s' % artist.name)
    session.query(Link).filter(Link.src_id == artist.id).delete()
    session.commit()

