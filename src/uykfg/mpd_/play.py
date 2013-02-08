
from logging import debug
from os.path import split, join
from time import sleep

from mpd import MPDClient
from random import choice
from sqlalchemy.sql.functions import random

from uykfg.music.db.catalogue import Album, Track
from uykfg.music.db.network import Link


def play_links(session, config):
    mpd = MPDClient()
    mpd.connect("localhost", 6600)
    while True:
        if empty(mpd):
            queue_random(mpd, config.mp3_path, session)
        else:
            last = almost_empty(mpd)
            if last: queue_next(mpd, session, config.mp3_path, last)
        sleep(10)

def empty(mpd):
    return not bool(mpd.playlistinfo(0))

def almost_empty(mpd):
    last = mpd.playlistinfo(0)
    if last and not mpd.playlistinfo(1): return last[0]
    else: return False

def queue_next(mpd, session, mp3_path, last):
    debug('next: %s' % last)
    track = find_track(session, mp3_path, last['file'])
    try: add_to_playlist(mpd, mp3_path, random_neighbour(session, track))
    except IndexError: queue_random(mpd, mp3_path, session)

def random_neighbour(session, track):
    neighbours = [src
                  for link in session.query(Link).filter(Link.dst == track.artist).all()
                  for src in link.src.tracks]
    debug('choice: %d %s' % (len(neighbours),
                             '; '.join('%s: %s' % (nbr.artist.name, nbr.name)
                                       for nbr in neighbours)))
    return choice(neighbours)

def add_to_playlist(mpd, mp3_path, track):
    path = join(track.album.path, track.file)[len(mp3_path):]
    if path.startswith('/'): path = path[1:]
    mpd.findadd('file', path)

def find_track(session, mp3_path, path):
    path, file = split(path)
    path = join(mp3_path, path)
    return session.query(Track).join(Album).filter(Album.path == path, Track.file == file).one()

def queue_random(mpd, mp3_path, session):
    track = session.query(Track).order_by('random()').limit(1).one()
    add_to_playlist(mpd, mp3_path, track)