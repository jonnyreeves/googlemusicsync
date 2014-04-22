#!/usr/bin/env python

import os
import errno
import json
import sys

from gmusicapi import Mobileclient
from operator import itemgetter
from appdirs import AppDirs
from gmusicapi import Musicmanager

APP_DIRS = AppDirs('GoogleMusicSync', 'Jonny Reeves')
DEFAULT_SYNC_COUNT = 200

def create_path_if_not_exist(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def download_track(mm, track, local_library):
	local_library = local_library.encode('utf-8')
	artist = track['artist'].encode('utf-8')
	album = track['album'].encode('utf-8')
	title = track['title'].encode('utf-8')

	print "Requesting {0} - {1} - {2}".format(artist, album, title)

	filename, audio = mm.download_song(track["id"])
	filename =  filename.encode('utf-8')

	target_dir = os.path.join(local_library, artist, album)
	target_path = os.path.join(target_dir, filename)

	create_path_if_not_exist(target_dir)

	print "Writing " + target_path
	with open(target_path, 'wb') as f:
		f.write(audio)

# Read configuration
try:
	cfg_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.json')
	print "Reading config from: " + cfg_file
	
	with open(cfg_file) as config_file:
		cfg = json.load(config_file)
		assert os.path.isdir(cfg['library'])
except:
	print "Failed to load configuration from settings.json"
	sys.exit();

# Login to GoogleMusic's Mobile API to get library metada
api = Mobileclient()
api.login(cfg["email"], cfg["password"])

# And now login to the Musicmanager to perform downloads.
mm = Musicmanager()
if (not mm.login()):
	mm.perform_oauth()

# Get the local copy of the track ids (these have been sync'd from remote)
create_path_if_not_exist(APP_DIRS.user_data_dir)
track_ids_file = os.path.join(APP_DIRS.user_data_dir, 'track_ids')
local_track_ids = None
print "Reading local Track Ids from: " + track_ids_file

try:
	with open (track_ids_file, "r") as file_handle:
		local_track_ids = json.loads(file_handle.read())
		print "Loaded {0} Track Id(s)".format(len(local_track_ids))
except IOError as io_error:
	if io_error.errno == errno.ENOENT:
		local_track_ids = []
		print "No local Track Ids found, nothing will be downloaded on this run"
	else:
		raise io_error

# Fetch the user's library from GoogleMusic and then flter by created timestamp to get
# a list of recently added tracks
print "Fetching library from Google Music"
library = api.get_all_songs()

sync_count = cfg['sync_count'] or DEFAULT_SYNC_COUNT
print "Filtering {0} most recently added tracks".format(cfg['sync_count'])
last_added = sorted(library, key=itemgetter('creationTimestamp'), reverse=True)[:sync_count]

tracks_by_id = {}
remote_track_ids = []

# Keep tracks in order to make the downloads appear in the expected order.
for track in last_added:
	track_id = track['id']
	tracks_by_id[track_id] = track
	remote_track_ids.append(track_id)

if (not remote_track_ids):
	print "No tracks fetched from Google Music API - exiting"
	sys.exit();

print "Fetched " + str(len(remote_track_ids)) + " Track Id(s) from Google Music"

# Compare the two and compute the delta to find new tracks
local_set = set(local_track_ids)
remote_set = set(remote_track_ids)
new_track_ids = list(remote_set.difference(local_set));

if ((local_track_ids) and (new_track_ids)):
	print "Found {0} new Track Id(s) on Google Music since last sync".format(len(new_track_ids))
	for track_id in new_track_ids:
		download_track(mm, tracks_by_id[track_id], cfg['library'])
else:
	print "No new tracks found."

if ((not local_track_ids) or (new_track_ids)):
	print "Writing {0} new Track Id(s) to {1}".format(len(new_track_ids), track_ids_file)
	with open(track_ids_file, 'w') as file_handle:
		file_handle.write(json.dumps(remote_track_ids))