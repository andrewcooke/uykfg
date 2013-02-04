
'''
For each directory under the root we first check if the directory is an
album (contains mp3s).  If it is, we check whether it already exists.
If it does exist, we check that it has not changed.  If it has changed we
delete it and continue as if new.  If it does not exist then we add it.

Artists are accumulated as we progress.  We call out to the tagger for
artist identification.

Once the root has been scanned any album that was not found is deleted.
Finally we can discard unused artists.
'''

from functools import partial
from logging import debug, warning
from os import walk
from os.path import join

from sqlalchemy.orm.exc import NoResultFound
from stagger.errors import NoTagError
from stagger.tags import read_tag

from uykfg.music.db.catalogue import Album, Track, Artist
from uykfg.support.io import getimtime
from uykfg.support.sequences import seq_and, lfilter


def scan(session, tagger, config):
    debug('retrieving all known albums from database.')
    remaining = dict((album.path, album) for album in session.query(Album).all())
    for path, files in candidates(config.mp3_path):
        scan_album(session, tagger, remaining, path, files)
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
            warning('empty directory at %s' % path)

def scan_album(session, tagger, remaining, path, files):
    debug('scanning album at %s' % path)
    if path in remaining:
        album = remaining[path]; del remaining[path]
        if is_unchanged_album(album, files): return
        delete_album(session, album)
    add_album(session, tagger, path, files)

def is_unchanged_album(album, files):
    if len(files) != len(album.tracks): return False
    tracks = dict((track.file, track) for track in album.tracks)
    return seq_and(map(partial(is_unchanged_track, album.path, tracks), files))

def is_unchanged_track(path, tracks, file):
    filepath = join(path, file)
    return file in tracks and tracks[file].modified == getimtime(filepath)

def delete_album(session, album):
    for track in album.tracks: session.delete(track)
    session.delete(album)
    debug('deleted %s' % album)

def add_album(session, tagger, path, files):
    data = list(file_data(path, files))
    titles = set(tag.album for (tag, file, modified) in data)
    if len(titles) == 1:
        # create album here so that is exists for the tracks to reference
        # we could use transactions, but simpler to delete if no tracks
        album = Album(name=titles.pop(), path=path)
        session.add(album)
        tracks = [add_track(session, tagger, album, tag, file, modified)
                  for (tag, file, modified) in data]
        if tracks:
            session.commit() # avoid too large a transaction
            debug('added %s' % album)
            return album
        else:
            session.delete(album)
            warning('no tracks for %s' % path)
    else:
        warning('ambiguous title(s) for %s (%s)' % (path, titles))

def file_data(path, files):
    for file in files:
        filepath = join(path, file)
        tag = get_tag(filepath)
        if tag:
            modified = getimtime(filepath)
            yield tag, file, modified

def add_track(session, tagger, album, tag, file, modified):
    artist = add_artist(session, tagger, album, tag)
    debug('creating track %s' % tag.track)
    return Track(artist=artist, album=album,
        number=tag.track, name=tag.title, file=file, modified=modified)

def add_artist(session, finder, album, tag):
    '''The music db reflects only the name from the ID3 tag, so there may
    be multiple artists with the same name.  The finder is responsible for
    disambiguation and may return either a new or an existing instance of
    Artist, as appropriate.

    But for efficiency we use the artist from the album, if it exists (ie
    for non-first tracks on single artist albums).'''
    try:
        debug('searching for artist %s in %s' % (tag.artist, album.name))
        return session.query(Artist).join('tracks', 'album')\
            .filter(Artist.name == tag.artist, Album.id == album.id).distinct().one()
    except NoResultFound:
        debug('delegating artist %s to finder' % tag.artist)
        return finder.find_artist(session, tag)

def cull_artists(session):
    for artist in session.query(Artist).filter(Artist.tracks == None).all():
        session.delete(artist)

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

