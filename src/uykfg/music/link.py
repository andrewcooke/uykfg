
from logging import debug
from sqlalchemy.sql.functions import random

from uykfg.music.db.catalogue import Artist
from uykfg.music.db.network import Link
from uykfg.support import twice_monthly


def link_all(session, linker):
    new_artists = session.query(Artist).filter(Artist.new == True)
    all_artists = session.query(Artist).order_by(random())
    have_new = new_artists.count()
    return link(session, linker, have_new, new_artists.all() if have_new else all_artists.all())

def link(session, linker, have_new, artists):
    for artist in artists:
        if have_new or twice_monthly():
            delete_src(session, artist)
            linker.link(session, artist)
            if have_new:
                artist.new = False
                session.commmit()
    debug('done!')

def delete_src(session, artist):
    debug('deleting links from %s' % artist.name)
    session.query(Link).filter(Link.src_id == artist.id).delete()
    session.commit()

