
from logging import debug
from random import choice

from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import random

from uykfg.music.db.catalogue import Track, Artist, Album
from uykfg.music.db.network import Link


def random_track(session):
    track = session.query(Track).order_by(random()).limit(1).one()
    debug('random: %s / %s' % (track.name, track.artist.name))
    return track

def neighbour_track(session, prev, max_links):
    neighbours = []
    # favour src as that gives more diversity (obscure bands tend to
    # be like common bands, but not vice-versa)
    neighbours = collect_src(session, prev, neighbours, max_links)
    neighbours = collect_dst(session, prev, neighbours, max_links)
    neighbours = collect_album(session, prev, neighbours, max_links)
    neighbours = collect_self(prev, neighbours, max_links)
    track = choice(expand_neighbours(neighbours, prev))
    debug('neighbour: %s / %s -> %s / %s' %
          (prev.name, prev.artist.name, track.name, track.artist.name))
    return track

def collect_src(session, track, neighbours, max_links):
    return accumulate(neighbours, max_links, 'src',
        (link.src for link in
         session.query(Link).filter(Link.dst == track.artist,
            Link.src != track.artist).order_by(random()).all()))

def collect_dst(session, track, neighbours, max_links):
    return accumulate(neighbours, max_links, 'dst',
        (link.dst for link in
         session.query(Link).filter(Link.src == track.artist,
             Link.dst != track.artist).order_by(random()).all()))

def accumulate(neighbours, max_links, label, artists):
    if len(neighbours) >= max_links: return neighbours
    for artist in artists:
        neighbours.append(artist)
        if len(neighbours) >= max_links: break
    debug('%s: %d' % (label, len(neighbours)))
    return neighbours

def collect_album(session, track, neighbours, max_links):
    artist1, track1, track2, artist2 = map(aliased, [Artist, Track, Track, Artist])
    return accumulate(neighbours, max_links, 'album',
        session.query(artist1).join(track1, Album, track2, artist2)\
                .filter(artist2.id == track.id, artist1.id != track.id)\
                .group_by(artist1.id).order_by(random()).all())

def collect_self(track, neighbours, max_links):
    if len(neighbours) < max_links:
        neighbours.append(track.artist)
        debug('self: %d', len(neighbours))
    return neighbours

def expand_neighbours(neighbours, prev):
    debug('selecting from: %s' % '; '.join(artist.name for artist in neighbours))
    return [track
            for artist in neighbours
            for track in artist.tracks
            if track != prev]
