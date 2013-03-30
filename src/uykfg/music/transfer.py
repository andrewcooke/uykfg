
from logging import debug
from os import mkdir, link
from os.path import join

from sqlalchemy.sql.functions import random

from uykfg.music.db.catalogue import Album


def transfer_size(session, config, root, limit):
    total = 0
    albums = iter(session.query(Album).order_by(random()).all())
    while total < limit:
        total += transfer_album(config, root, next(albums))

def transfer_album(config, root, album):
    assert album.path.startswith(config.mp3_path), 'bad path: %s' % album.path
    delta = album.path[len(config.mp3_path):]
    destn = join(root, delta)
    return sum(map(transfer_track(album.path, destn), album.tracks))

def transfer_track(src, dst):
    debug('%s => %s' % (src, dst))
    mkdir(dst)
    def transfer(track):
        src2 = join(src, track.path)
        dst2 = join(dst, track.path)
        debug('%s -> %s' % (src2, dst2))
        link(src2, dst2)
        return track.size
