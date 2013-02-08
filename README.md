
Uykfg - Echonest MPD Client
===========================

Trying again in the Uykf line.  This time as a client for mpd.

Forked off Uykff.

This now works.  It contains three scripts:

* scan.sh will scan a music collection and identify the artists by checking
  against EchoNest;

* link.sh will connect related artists using the metadata from EchoNest;

* play.sh will watch mpd and and a new, related, track whenever there is
  only a single track on the playlist.  It will also add a random track when
  the playlist is empty.

However, the number of calls made to EchoNest is huge when first run (the
scan and link scripts; even though the calls are aggressively cached it
takes days to get the data for my music collection).  So this is not a good
use of EchoNest and won't scale well.

If, despite that, you want to use this code, please email me at
andrew@acooke.org for the ID (I think this idea is that the program should
use a single ID in the API; it is designed to self-throttle if multiple
users are running).

