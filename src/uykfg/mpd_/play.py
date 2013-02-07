
from time import sleep

from mpd import MPDClient


def play_links(session):
    mpd = MPDClient()
    mpd.connect("localhost", 6600)
    while True:
        if almost_empty(mpd): queue_next(mpd, session)
        sleep(10)

def almost_empty(mpd):
    print(mpd.playlistinfo(1))
    return False

def queue_next(mpd, session):
    pass
