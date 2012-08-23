
'''
For each directory under the root we first check if the directory is an
album (contains mp3s).  If it is, we check whether it already exists.
If it does exist, we check that it has not changed.  If it has changed we
delete it and continue as if new.  If it does not exist then we add it.

Artists are accumulated as we progress.  We call out to additional services
for artist identification and tags.

Once the root has been scanned any album that was not found is deleted.
Finally we can discard unused artists.
'''

from datetime import datetime
from functools import partial
from logging import debug, warning
from operator import attrgetter
from os import walk
from os.path import join, getmtime

from sqlalchemy.orm.exc import NoResultFound
from stagger.errors import NoTagError
from stagger.tags import read_tag

from uykff.core.db.catalogue import Album, Track, Artist
from uykff.core.support.sequences import seq_and, lfilter, lmap


def scan(session, config):
    debug('retrieving all known albums from database.')
    remaining = dict((album.path, album) for album in session.query(Album).all())
    for path, files in candidates(config.mp3_path):
        scan_album(session, remaining, path, files)
    for path in remaining: delete_album(session, remaining[path])
    cull_artists(session)
    session.commit()

def candidates(root):
    for path, dirs, files in walk(root):
        files = lfilter(lambda file: file.endswith('.mp3'), files)
        if files:
            if dirs:
                warning('ignoring sub-directories in %s' % path)
                del dirs
            yield path, files
        elif not dirs:
            warning('ignoring empty directory at %s' % path)

def scan_album(session, remaining, path, files):
    debug('scanning album at %s' % path)
    if path in remaining:
        album = remaining[path]; del remaining[path]
        if unchanged_album(album, files): return
        delete_album(session, album)
    add_album(session, path, files)

def unchanged_album(album, files):
    if len(files) != len(album.tracks): return False
    tracks = dict((track.file, track) for track in album.tracks)
    return seq_and(map(partial(unchanged_track, album.path, tracks), files))

def unchanged_track(path, tracks, file):
    filepath = join(path, file)
    return file in tracks and \
           tracks[file].modified == datetime.fromtimestamp(getmtime(filepath))

def delete_album(session, album):
    for track in album.tracks: session.delete(track)
    session.delete(album)
    debug('deleted %s' % album)

def add_album(session, path, files):
    data = list(file_data(path, files))
    titles = set(tag.album for (tag, file, modified) in data)
    if len(titles) == 1:
        tracks = [add_track(session, tag, file, modified)
                  for (tag, file, modified) in data]
        if tracks:
            album = Album(name=titles.pop(), tracks=tracks, path=path)
            session.add(album)
            debug('added %s' % album)
            return album
        else:
            warning('no tracks for %s' % path)
    else:
        warning('bad title(s) for %s (%s)' % (path, titles))

def file_data(path, files):
    for file in files:
        filepath = join(path, file)
        tag = get_tag(filepath)
        modified = datetime.fromtimestamp(getmtime(filepath))
        if tag: yield tag, file, modified
        else: warning('no ID3 for %s' % filepath)

def add_track(session, tag, file, modified):
    artist = add_artist(session, tag)
    return Track(artist=artist, number=tag.track, name=tag.title, file=file,
        modified=modified)

def add_artist(session, tag):
    try:
        return session.query(Artist).filter(Artist.name == tag.artist).one()
    except NoResultFound:
        artist = Artist(name=tag.artist)
        session.add(artist) # so we can find it before commit at end
        return artist

def cull_artists(session):
    # TODO outer join w tracks gives null track
    pass

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

