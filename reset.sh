#!/bin/bash

sqlite3 ~/.uykfgdb <<EOF
drop table music_links;
drop table nest_artists_and_music_artists;
drop table nest_artists;
drop table music_artists;
drop table music_albums;
drop table music_tracks;
drop table music_artists_and_music_tags;
drop table music_tags;
.tables
EOF
