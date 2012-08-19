
Uykff - a music manager
=======================

This project is currently under development.
This "readme" is an overview of the project aims and general design.
It will be replaced with an introduction and install document once the
project is close to completion.

Background
----------

Uykff is the third of a series of programs (following uykfd and uykfe) 
that calculate on-the-fly playlists for a collection of mp3 files.

At a high level this version will be:

* easier to use;

* more enjoyable to use;

* more expandable.

At a lower level these aims will be met by:

* providing a web interface;

* making that interface attractive;

* supporting a variety of algorithms (for playlist generation) and
  targets (for streaming music or writing playlists).

Plugins
-------

Based on http://martyalchin.com/2008/jan/10/simple-plugin-framework/
the central core (which will be what, exactly? an MVC based around a
database of tracks, I guess - but why isn't *that* a plugin?) will
delegate to arbitrary implementations of interfaces.

Plugins everywhere!

For example, playlist generation might use a combination of
suggestions and filtering, where filtering is based on the combined
votes of multiple algorithms.

Playlist streaming could be to an m3u file, a directory with links to
individual tracks (for copying to RockBox), streaming to a uPNP
device, or interacting with squeeze server.

Interface
---------

The somewhat anarchic (and likely naive, but we'll cross that when we
come to it) vision of plugins seems like it will cause problems in the
interface.  One possible solution is to structure the interface around
a number of simple ideas (artist view, album view, etc) which use
something like the jQuery Mason plugin to "tile" displays from
plugins.  This could turn a negative into a positive...

Metadata 
--------

Previous iterations used Last.fm.  That doesn't seem to me to have the
greatest future.  So it might be worth trying echonest instead
(plugins!).

Incremental Algorithms
----------------------

A major issue with uykfe is the length of time required to regenerate
the data when new music is added to the system.  This is largely
because the approach relies on a single graph constructed across all
data using a "global" process.

So instead we must either avoid a global graph completely, or
construct the graph in an incremental (local) manner.
