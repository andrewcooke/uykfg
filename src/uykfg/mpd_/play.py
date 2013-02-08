
from logging import debug
from os.path import split, join
from time import sleep

from mpd import MPDClient
from random import choice

from uykfg.music.db.catalogue import Album, Track
from uykfg.music.db.network import Link
from uykfg.music.play import random_track


def play_links(session, config):
    mpd = MPDClient()
    mpd.connect("localhost", 6600)
    while True:
        if empty(mpd):
            queue(mpd, config.mp3_path, random_track(session))
        else:
            last = almost_empty(mpd)
            if last: queue(mpd, config.mp3_path,
                           neighbour_track(session, last, config.max_links))
        sleep(1)

def empty(mpd):
    return not bool(mpd.playlistinfo(0))

def almost_empty(mpd):
    last = mpd.playlistinfo(0)
    if last and not mpd.playlistinfo(1): return last[0]
    else: return False

def queue(mpd, mp3_path, track):
    path = join(track.album.path, track.file)[len(mp3_path):]
    if path.startswith('/'): path = path[1:]
    mpd.findadd('file', path)

