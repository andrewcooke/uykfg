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
            penultimate = almost_empty(mpd)
            if penultimate: queue_next(mpd, session, penultimate)
        sleep(10)

def empty(mpd):
    return not bool(mpd.playlistinfo(0))

def almost_empty(mpd):
    penultimate = mpd.playlistinfo(1)
    if penultimate:
        penultimate = penultimate[0]
        if not mpd.playlistinfo(1): return penultimate
    return False

def queue_next(mpd, session, penultimate):
    debug('next')

def queue_random(mpd, session):
    debug('random')
