from logging import debug
from time import sleep

from mpd import MPDClient


def play_links(session):
    mpd = MPDClient()
    mpd.connect("localhost", 6600)
    while True:
        if empty(mpd):
            queue_random(mpd, session)
        else:
            last = almost_empty(mpd)
            if last: queue_next(mpd, session, last)
        sleep(10)

def empty(mpd):
    return not bool(mpd.playlistinfo(0))

def almost_empty(mpd):
    last = mpd.playlistinfo(0)
    if last and not mpd.playlistinfo(1): return last[0]
    else: return False

def queue_next(mpd, session, last):
    debug('next: %s' % last)

def queue_random(mpd, session):
    debug('random')
