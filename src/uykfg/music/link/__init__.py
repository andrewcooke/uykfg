
from logging import debug
from sqlalchemy.orm import aliased

from uykfg.music.db.catalogue import Artist, Track, Album
from uykfg.music.db.network import Link


def link_all(session, linker):
    for artist in session.query(Artist).all():
        delete_src(session, artist)
        link_same_album(session, artist)
        linker.link(session, artist)
    debug('done!')

def delete_src(session, artist):
    debug('deleting links from %s' % artist.name)
    session.query(Link).filter(Link.src_id == artist.id).delete()
    session.commit()

def link_same_album(session, src):
    artist1, track1, track2, artist2 = map(aliased, [Artist, Track, Track, Artist])
    commit = False
    for dst in session.query(artist1).join(track1, Album, track2, artist2)\
            .filter(artist2.id == src.id, artist1.id != artist2.id)\
            .group_by(artist1.id).all():
        debug('linking %s to %s via common album' % (src.name, dst.name))
        session.add(Link(src=src, dst=dst))
        commit = True
    if commit: session.commit()
