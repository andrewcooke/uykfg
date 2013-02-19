
from sys import argv
from sqlalchemy.orm.exc import NoResultFound

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist, Album, Track
from uykfg.nest.db import NestArtist
from uykfg.support.configure import Config


def show(names):
    config = Config.default()
    session = startup(config)
    for name in names:
        for artist in session.query(Artist).filter(Artist.name == name).all():
            try: nest_artist = session.query(NestArtist).filter(NestArtist.artists.any(id=artist.id)).one()
            except NoResultFound: nest_artist = 'no nest artist'
            print('%s (%s)' % (artist.name, nest_artist.name))
            print(' tags:\n  %s' % ' '.join('"%s"' % tag.text for tag in artist.tags))
            print(' albums:')
            for album in session.query(Album).join(Track).join(Artist)\
                    .filter(Artist.id == artist.id).distinct().all():
                print('  %s' % album.name)


if __name__ == '__main__':
    show(argv[1:])
