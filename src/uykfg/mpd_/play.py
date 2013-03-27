
from logging import warning
from os.path import split, join
from time import sleep

from mpd import MPDClient, ConnectionError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import NoResultFound
from uykfg.music.db.catalogue import Track, Album

from uykfg.music.play import random_track, neighbour_track


def play_links(session, config):
    while True:
        try:
            mpd = MPDClient()
            mpd.connect("localhost", 6600)
            while True:
                if empty(mpd):
                    queue(mpd, config.mp3_path, random_track(session))
                else:
                    last = almost_empty(mpd)
                    if last: queue(mpd, config.mp3_path,
                                   neighbour_track(session,
                                        find_track(session, config.mp3_path, last),
                                        config.max_links))
                sleep(0.1)
        except KeyboardInterrupt as e: raise e
        except Exception as e:
            warning(e)
            sleep(10)

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

