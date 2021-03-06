
'''
For each directory under the root we first check if the directory is an
album (contains mp3s).  If it is, we check whether it already exists.
If it does exist, we check that it has not changed.  If it has changed we
delete it and continue as if new.  If it does not exist then we add it.

Artists are accumulated as we progress.  We call out to the finder for
artist identification.

Once the root has been scanned any album that was not found is deleted.
Finally we can discard unused artists.

It's important that artists are not deleted with albums, because the link
information is associated with artists (and would need to be rebuilt if
artists were deleted).
'''

from functools import partial
from logging import debug, warning, error
from os import walk
from os.path import join

from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound
from stagger.errors import NoTagError
from stagger.tags import read_tag

from uykfg.music.db.catalogue import Album, Track, Artist
from uykfg.music.db.network import Link
from uykfg.music.db.tags import Tag
from uykfg.nest.finder import FinderError
from uykfg.support import twice_monthly
from uykfg.support.io import getimtime, getimsize
from uykfg.support.sequences import seq_and, lfilter


def scan_all(session, finder, config, all):
    debug('retrieving all known albums from database.')
    remaining = dict((album.path, album) for album in session.query(Album).all())
    debug('scanning %s albums.' % ('all' if all else 'changed'))
    for path, files in candidates(config.mp3_path):
        scan_album(session, finder, remaining, path, files, all)
    for path in remaining: delete_album(session, remaining[path])
    cull_albums(session)
    cull_artists(session, finder)
    cull_tags(session)
    debug('done!')

def candidates(root):
    debug('scanning %s' % root)
    for path, dirs, files in walk(root):
        files = lfilter(lambda file: file.endswith('.mp3'), files)
        if files:
            if dirs:
                warning('ignoring sub-directories in %s' % path)
                del dirs
            yield path, files
        elif not dirs:
            warning('empty directory at %s' % path)

def scan_album(session, finder, remaining, path, files, all):
    debug('scanning album at %s' % path)
    if path in remaining:
        album = remaining[path]; del remaining[path]
        if not all and is_unchanged_album(session, finder, album, files): return
        delete_album(session, album)
    add_album(session, finder, path, files)

def is_unchanged_album(session, finder, album, files):
    if twice_monthly(): return False # twice a month, check anyway
    if len(files) != len(album.tracks): return False
    if finder.missing_artist(session, album.tracks): return False
    tracks = dict((track.file, track) for track in album.tracks)
    return seq_and(map(partial(is_unchanged_track, album.path, tracks), files))

def is_unchanged_track(path, tracks, file):
    filepath = join(path, file)
    return file in tracks and tracks[file].modified == getimtime(filepath)

def delete_album(session, album):
    for track in album.tracks: session.delete(track)
    session.delete(album)
    debug('deleted %s' % album)

def add_album(session, finder, path, files):
    data = list(file_data(path, files))
    titles = set(tag.album for (tag, file, modified, size) in data)
    if len(titles) == 1:
        try:
            # transaction starts here.
            # create album so that is exists for the tracks to reference
            album = Album(name=titles.pop(), path=path)
            session.add(album)
            # then add tracks
            tracks = list(add_tracks(session, finder, album, data))
            if tracks:
                # commit on success
                session.commit()
                debug('added %s' % album)
                return
            else:
                warning('no tracks for %s' % path)
        except KeyboardInterrupt as e: raise e
        except Exception as e:
            # don't access objects here as they may raise more errors
            error('error adding %s: %s' % (path, e))
        # if no tracks, or error, discard
        session.rollback()
    else:
        warning('ambiguous title(s) for %s (%s)' % (path, titles))

def file_data(path, files):
    for file in files:
        filepath = join(path, file)
        tag = get_tag(filepath)
        if tag:
            modified = getimtime(filepath)
            size = getimsize(filepath)
            yield tag, file, modified, size

def add_tracks(session, finder, album, data):
    retry0, retry1, retry2 = [], [], []
    single_artist = len(set(d[0].artist for d in data)) == 1
    # first, try identify artist with track
    found = False
    for (tag, file, modified, size) in data:
        if single_artist and found: # we can reuse this
            retry0.append((tag, file, modified, size))
        else:
            try:
                yield add_single_track(session, finder, album, tag, file, modified, size)
                found = True
            except FinderError: retry0.append((tag, file, modified, size))
    # now check to see if we identified on a later track (reuse above)
    for (tag, file, modified, size) in retry0:
        try: yield add_album_track(session, album, tag, file, modified, size)
        except NoResultFound: retry1.append((tag, file, modified, size))
    # use artist name alone
    for (tag, file, modified, size) in retry1:
        try: yield add_artist(session, finder, album, tag, file, modified, size)
        except FinderError: retry2.append((tag, file, modified, size))
    # if we failed for the entire album, and have a single artist, try combining tracks
    if len(retry2) == len(data) and len(data) > 1 and \
       len(set(d[0].artist for d in data)) == 1:
        for track in add_album_tracks(session, finder, album, retry2):
            yield track
            retry2 = [] # we found the artist
    # finally, construct new artist local to this album
    if retry2:
        warning('%d unconfirmed tracks in %s' % (len(retry2), album.path))
        local = {}
        for (tag, file, modified, size) in retry2:
            if tag.artist in local: artist = local[tag.artist]
            else:
                artist=finder.local_artist(session, tag.artist)
                local[tag.artist] = artist
            yield add_track(artist, tag.title, tag.track, album, file, modified, size)

def add_single_track(session, finder, album, tag, file, modified, size):
    try: artist = get_album_artist(session, tag.artist, album)
    except NoResultFound: artist = add_track_artist(session, finder, tag)
    return add_track(artist, tag.title, tag.track, album, file, modified, size)

def get_album_artist(session, name, album):
    return session.query(Artist).join('tracks', 'album')\
    .filter(Artist.name == name, Album.id == album.id).distinct().one()

def add_track_artist(session, finder, tag):
    debug('delegating artist %s, track %s to finder' % (tag.artist, tag.title))
    return finder.find_track_artist(session, tag.artist, tag.title)

def add_album_track(session, album, tag, file, modified, size):
    artist = get_album_artist(session, tag.artist, album)
    return add_track(artist, tag.title, tag.track, album, file, modified, size)

def add_artist(session, finder, album, tag, file, modified, size):
    debug('delegating artist %s to finder' % tag.artist)
    artist = finder.find_artist(session, tag.artist)
    return add_track(artist, tag.title, tag.track, album, file, modified, size)

def add_track(artist, title, number, album, file, modified, size):
    debug('creating track %s' % title)
    return Track(artist=artist, album=album,
        number=number, name=title, file=file, modified=modified, size=size)

def add_album_tracks(session, finder, album, data):
    titles = [tag.title for (tag, file, modified, size) in data]
    try:
        artist = finder.find_tracks_artist(session, data[0][0].artist, titles)
        for (tag, file, modified, size) in data:
            yield add_track(artist, tag.title, tag.track, album, file, modified, size)
    except FinderError:
        warning('no artist found for %s' % album.path)

def cull_artists(session, finder):
    artists = session.query(Artist).filter(Artist.tracks == None)
    warning('removing %d unused artists' % artists.count())
    for artist in artists.all():
        debug('removing %s' % artist.name)
        session.query(Link).filter(or_(Link.src == artist, Link.dst == artist)).delete()
        for tag in artist.tags: artist.tags.remove(tag)
        finder.delete_artist(session, artist)
        session.delete(artist)
    session.commit()

def cull_albums(session):
    albums = session.query(Album).filter(Album.tracks == None)
    warning('removing %d unused albums' % albums.count())
    albums.delete(synchronize_session=False)
    session.commit()

def cull_tags(session):
    tags = session.query(Tag).filter(Tag.artists == None)
    warning('removing %d unused tags' % tags.count())
    tags.delete(synchronize_session=False)
    session.commit()

def get_tag(path):
    try:
        tag = read_tag(path)
        if tag and tag.artist and tag.title:
            return tag
        else:
            warning('no ID3 for %s.' % path)
    except UnicodeEncodeError as e:
        warning('cannot encode ID3 for %s (%s)' % (path, e))
    except NoTagError as e:
        warning('cannot read ID3 for %s (%s)' % (path, e))
    except ValueError as e:
        warning('cannot read ID3 for %s (%s)' % (path, e))

