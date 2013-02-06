#!/bin/bash

sqlite3 ~/.uykfgdb <<EOF
drop table nest_artists;
drop table music_artists;
drop table music_albums;
drop table music_tracks;
.tables
EOF
