
from logging import debug
from os import link, makedirs
from os.path import join

from sqlalchemy.sql.functions import random

from uykfg.music.db.catalogue import Album


def transfer_size(session, config, root, limit):
    total = 0
    albums = iter(session.query(Album).order_by(random()).all())
    while total < limit:
        total += transfer_album(config, root, next(albums))
    debug('transferred %.1f GB' % (total / 1e9))

def transfer_album(config, root, album):
    assert album.path.startswith(config.mp3_path), 'bad path: %s' % album.path
    delta = album.path[len(config.mp3_path):]
    while delta.startswith('/'): delta = delta[1:]
    destn = join(root, delta)
    return sum(map(transfer_track(album.path, destn), album.tracks))

def transfer_track(src, dst):
    debug('%s => %s' % (src, dst))
    makedirs(dst)
    def transfer(track):
        src2 = join(src, track.file)
        dst2 = join(dst, track.file)
        debug('%s -> %s' % (src2, dst2))
        link(src2, dst2)
        return track.size
    return transfer
