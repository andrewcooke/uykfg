
from logging import debug
from sqlalchemy import alias

from uykfg.music.db.catalogue import Artist, Track, Album
from uykfg.music.db.network import Link


def link_all(session, linker):
    for artist in session.query(Artist).all():
        delete_src(session, artist)
        link_same_album(session, artist)
        linker.link(session, artist)
    debug('done!')

def delete_src(session, artist):
    session.query(Link).filter(Link.src_id == artist.id).delete()
    session.commit()

def link_same_album(session, src):
    artist1, tracks1, album, tracks2, artist2 = map(alias, [Artist, Track, Album, Track, Artist])
    for dst in session.query(artist1).join(tracks1, album, tracks2, artist2)\
            .filter(artist1.id == src.id, artist1.id != artist2.id)\
            .select(artist2.distinct()).all():
        print(dst)
