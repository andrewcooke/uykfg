
from logging import debug, warning
from sqlalchemy.sql.functions import random

from uykfg.music.db.catalogue import Artist
from uykfg.music.db.network import Link
from uykfg.support import twice_monthly


def link_all(session, linker):
    have_new = session.query(Artist).filter(Artist.new == True).count()
    if have_new: warning('new artists; re-linking all')
    for artist in session.query(Artist).order_by(random()).all():
        if have_new or twice_monthly():
            delete_src(session, artist)
            linker.link(session, artist)
            if have_new:
                artist.new = False
                session.commit()
    debug('done!')

def delete_src(session, artist):
    debug('deleting links from %s' % artist.name)
    session.query(Link).filter(Link.src_id == artist.id).delete()
    session.commit()

