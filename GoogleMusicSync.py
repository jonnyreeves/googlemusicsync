import os
import errno
import json
import sys

from gmusicapi import Mobileclient
from operator import itemgetter
from appdirs import AppDirs
from gmusicapi import Musicmanager

MUSIC_LIBRARY="/Users/jonny/Desktop/foo"
APP_DIRS = AppDirs('GoogleMusicSync', 'Jonny Reeves')
RECENTLY_ADDED_SIZE = 100

def create_path_if_not_exist(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def download_track(mm, track):
	print "Downloading {0}/{1}/{2} to {3}".format(track['artist'], track['album'], track['title'], MUSIC_LIBRARY)

	filename, audio = mm.download_song(track["id"])
	target_dir = os.path.join(MUSIC_LIBRARY, track["artist"], track["album"])
	target_path = os.path.join(target_dir, filename)
	create_path_if_not_exist(target_dir)

	print "Writing " + target_path
	with open(target_path, 'wb') as f:
		f.write(audio)


# Login to GoogleMusic's Mobile API to get library metada
api = Mobileclient()
api.login('john@jonnyreeves.co.uk', 'hcctlielengpllcp')

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
		print "Loaded " + str(len(local_track_ids)) + " Track Id(s) from " + track_ids_file
except IOError as io_error:
	if io_error.errno == errno.ENOENT:
		local_track_ids = []
		print "No local Track Ids found, nothing will be downloaded on this run"
	else:
		raise io_error

# Fetch the user's library from GoogleMusic and then flter by created timestamp to get
# a list of recently added tracks
print "Fetching the last {0} tracks from Google Music".format(RECENTLY_ADDED_SIZE)
last_added = sorted(api.get_all_songs(), key=itemgetter('creationTimestamp'), reverse=True)[:RECENTLY_ADDED_SIZE]
tracks_by_id = {}

for track in last_added:
	tracks_by_id[track['id']] = track

remote_track_ids = list(tracks_by_id.keys())
if (not remote_track_ids):
	print "No tracks fetched from Google Music API - exiting"
	sys.exit();

print "Fetched " + str(len(remote_track_ids)) + " Track Id(s) from Google Music"

# Compare the two and compute the delta to find new tracks
local_set = set(local_track_ids)
remote_set = set(remote_track_ids)
new_track_ids = list(remote_set.difference(local_set));

if ((local_track_ids) and (new_track_ids)):
	print "Found " + str(len(new_track_ids)) + " new Track Id(s) on Google Music"

	# Download each track
	for track_id in new_track_ids:
		download_track(mm, tracks_by_id[track_id])

else:
	print "No new tracks found."

if ((not local_track_ids) or (new_track_ids)):
	# Save the updated local track list.
	print "Writing " + str(len(new_track_ids)) + " new Track Id(s) to: " + track_ids_file
	with open(track_ids_file, 'w') as file_handle:
		file_handle.write(json.dumps(remote_track_ids))




