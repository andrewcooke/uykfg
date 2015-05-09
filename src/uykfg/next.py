
from logging import debug
from sys import argv
from os.path import split, join
from sqlalchemy import or_

from sqlalchemy.sql.functions import random

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Track, Artist, Album
from uykfg.music.db.tags import Tag
from uykfg.music.play import all_neighbours
from uykfg.support.configure import Config


def parse_constraints(constraints):
    count, inc_tag, exc_tag, inc_artist, exc_artist, path = 1, [], [], [], [], None
    for constraint in constraints:
        debug("parsing %s" % constraint)
        try:
            count = int(constraint)
        except ValueError:
            if len(constraint) < 4 or constraint[1] != ':':
                raise Exception('Bad format: %s' % constraint)
            elif constraint.startswith('a'): inc_artist.append(constraint[2:])
            elif constraint.startswith('A'): exc_artist.append(constraint[2:])
            elif constraint.startswith('t'): inc_tag.append(constraint[2:])
            elif constraint.startswith('T'): exc_tag.append(constraint[2:])
            elif constraint.startswith('u') and not path:
                track = constraint[2:]
                if track.startswith('file://'): track = track[7:]
            else: raise Exception('Bad constraint: %s' % constraint)
    return count, inc_tag, exc_tag, inc_artist, exc_artist, path

def next(constraints):
    config = Config.default()
    session = startup(config)
    count, inc_tag, exc_tag, inc_artist, exc_artist, path = parse_constraints(constraints)
    tracks = session.query(Track).join(Artist)
    if inc_artist:
        query = session.query(Artist.id).filter(or_(Artist.name.like(name) for name in inc_artist))
        tracks = tracks.filter(Artist.id.in_(query))
    if exc_artist:
        query = session.query(Artist.id).filter(or_(Artist.name.like(name) for name in exc_artist))
        tracks = tracks.filter(~Artist.id.in_(query))
    if inc_tag:
        query = session.query(Artist.id).join(Artist.tags).filter(or_(Tag.text.like(tag) for tag in inc_tag))
        tracks = tracks.filter(Artist.id.in_(query))
    if exc_tag:
        query = session.query(Artist.id).join(Artist.tags).filter(or_(Tag.text.like(tag) for tag in exc_tag))
        tracks = tracks.filter(~Artist.id.in_(query))
    if path:
        (path, file) = split(path)
        track = session.query(Track).join(Album).filter(Album.path == path, Track.file == file).one()
        neighbours = all_neighbours(session, track, config.max_links)
        tracks = tracks.filter(Track.id.in_(neighbours))

    for track in tracks.order_by(random()).limit(count):
        print(join(track.album.path, track.file))


if __name__ == '__main__':
    next(argv[1:])

