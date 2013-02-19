
from mpd import MPDClient

from uykfg.mpd_.play import queue


def add_tracks(session, config, tracks):
    mpd = MPDClient()
    mpd.connect("localhost", 6600)
    for track in tracks:
        queue(mpd, config.mp3_path, track)
