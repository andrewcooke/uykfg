
from logging import debug
from random import choice

from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import random

from uykfg.music.db.catalogue import Track, Artist, Album
from uykfg.music.db.network import Link


def random_track(session):
    return session.query(Track).order_by(random()).limit(1).one()

def neighbour_track(session, track, max_links):
    neighbours = []
    neighbours = collect_src(session, track, neighbours, max_links)
    neighbours = collect_dst(session, track, neighbours, max_links)
    neighbours = collect_album(session, track, neighbours, max_links)
    neighbours = collect_self(track, neighbours, max_links)
    return choice(expand_neighbours(neighbours, track))

def collect_src(session, track, neighbours, max_links):
    return accumulate(neighbours, max_links,
        (link.src for link in
         session.query(Link).filter(Link.dst == track.artist,
            Link.src != track.artist).order_by(random()).all()))

def collect_dst(session, track, neighbours, max_links):
    return accumulate(neighbours, max_links,
        (link.dst for link in
         session.query(Link).filter(Link.src == track.artist,
             Link.dst != track.artist).order_by(random()).all()))

def accumulate(neighbours, max_links, artists):
    if len(neighbours) >= max_links: return neighbours
    for artist in artists:
        neighbours.append(artist)
        if len(neighbours) >= max_links: return neighbours
    return neighbours

def collect_album(session, track, neighbours, max_links):
    artist1, track1, track2, artist2 = map(aliased, [Artist, Track, Track, Artist])
    return accumulate(neighbours, max_links,
        session.query(artist1).join(track1, Album, track2, artist2)\
                .filter(artist2.id == track.id, artist1.id != track.id)\
                .group_by(artist1.id).order_by(random()).all())

def collect_self(track, neighbours, max_links):
    if len(neighbours) < max_links: neighbours.append(track.artist)
    return neighbours

def expand_neighbours(neighbours, prev):
    debug('selecting from %s' % ', '.join(artist.name for artist in neighbours))
    return [track
            for artist in neighbours
            for track in artist.tracks
            if track != prev]
