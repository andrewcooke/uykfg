
Uykfg - Echonest MPD Client
===========================

A playlist generator for mpd, using metadata from EchoNest.

This assumes that music is stored in mp3s, with ID3 metadata, grouped in
directories by album, with albums grouped in directories by artist.

Warning
-------

The number of calls made to EchoNest is huge when first run (the scan and link
scripts; even though the calls are aggressively cached it takes days to get
the data for my music collection).  So this is not a good use of EchoNest and
won't scale well.

Because of the above (and, you know, laziness), this project is not packaged
for easy use.  On the other hand, I think it's pretty awesome and use it all
the time.

So if you want to use this code, and are happy getting a clone running (it's
pretty much trivial if you're an experience Python programmer) please email me
at andrew@acooke.org for the ID (I think the idea is that the program should
use a single ID in the API; it is designed to self-throttle if multiple users
are running).

Maintenance Scripts
-------------------

* `scan.sh` - This reads the directories below the root (set in the
  configuration file), checking for new data.  ID3 data for new tracks (and,
  randomly, some old tracks) are read and cross-referenced against the
  EchoNest database.

* `link.sh` - This checks for links between the artists found, using
  EchoNest's related artists.  If new artists were found via scan.sh then all
  artists are updated, otherwise only a random selection.

* `update.sh` - Calls the above two scripts; expected to be called each night
  to update the local database as necessary.

* `reset.sh` - Wipes the database (except for the EchoNest cache).

A note on caching - all calls to EchoNest are cached and expire over a random
period (between 0 and 30 days).  This, together with random re-processing,
means that updated data in EchoNest is slowly absorbed into the local
database (typically within a month).

Playlist Script
---------------

`play.sh` watches the mpd queue and takes action in two cases:

* when the queue is empty, a new, random track is added (but not played);

* when the queue contains a single entry a new, related track is appended.

The intention is that this script runs continually in the background.
Selecting a random "starting point" is then possible by clearing the queue.
Pressing play then generates a continuous playlist, song by related song.  But
if other music is selected then the functionality is automatically suppressed
(until the final track is played, at which point another will be added).

Tag Scripts
-----------

Popular tags from EchoNest are also stored in the database.  These can be used
as follows:

* `ushow` - Displays the tags (and other info) for a given artist.

* `uwho` - Shows the artists that match a given tag.

* `uadd` - Adds random tracks from artists that match the given tag.

Tags can be combined and exclude with a `-` prefix.  So `uadd 20 blues -pop`
will add 20 tracks from artists that are tagged with "blues" but *not* tagged
with "pop".

PMP script
----------

`transfer.sh` will create a directory of links to tracks of a given size,
selected at random, that can then be compied to a PMP (iPod etc).
