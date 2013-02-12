
from logging import warning
from os.path import split, join
from time import sleep

from mpd import MPDClient
from sqlalchemy.exc import OperationalError
from uykfg.music.db.catalogue import Track, Album

from uykfg.music.play import random_track, neighbour_track


def play_links(session, config):
    mpd = MPDClient()
    mpd.connect("localhost", 6600)
    while True:
        try:
            if empty(mpd):
                queue(mpd, config.mp3_path, random_track(session))
            else:
                last = almost_empty(mpd)
                if last: queue(mpd, config.mp3_path,
                               neighbour_track(session,
                                    find_track(session, config.mp3_path, last),
                                    config.max_links))
        except OperationalError as e:
            warning(e)
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

def find_track(session, mp3_path, track):
    path, file = split(track['file'])
    path = join(mp3_path, path)
    return session.query(Track).join(Album).filter(Album.path == path, Track.file == file).one()

