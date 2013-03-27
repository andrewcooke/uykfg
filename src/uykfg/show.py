
from sys import argv
from sqlalchemy.orm.exc import NoResultFound

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist, Album, Track
from uykfg.music.db.network import Link
from uykfg.nest.db import NestArtist
from uykfg.support.configure import Config


def show(names):
    config = Config.default()
    session = startup(config)
    for name in names:
        for artist in session.query(Artist).filter(Artist.name == name).all():
            try:
                nest_artist = session.query(NestArtist).filter(NestArtist.artists.any(id=artist.id)).one()
                print('%s (%s)' % (artist.name, nest_artist.name))
            except NoResultFound:
                nest_artist = None
                print('%s' % artist.name)
            print(' tags:\n  %s' % ' '.join('"%s"' % tag.text for tag in artist.tags))
            print(' albums:')
            for album in session.query(Album).join(Track).join(Artist)\
                    .filter(Artist.id == artist.id).distinct().all():
                print('  %s' % album.name)
            if nest_artist:
                for other in nest_artist.artists:
                    if other != artist:
                        for album in session.query(Album).join(Track).join(Artist)\
                                .filter(Artist.id == other.id).distinct().all():
                            print('  %s (as %s)' % (album.name, other.name))
                        
            print(' linked to:')
            for link in session.query(Link).filter(Link.src == artist):
                print('  %s' % link.dst.name)
            print(' linked from:')
            for link in session.query(Link).filter(Link.dst == artist):
                print('  %s' % link.src.name)


if __name__ == '__main__':
    show(argv[1:])
