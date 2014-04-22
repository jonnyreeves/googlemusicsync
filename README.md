# Google Music Sync
A quick and dirty python script for downloading the most recently added tracks in your Google Music library.

## Why?
I uploaded my music collection to Google Music a few months back but found that my local library was slowly difting out of sync as I purchased now tracks on Google Music / uploaded them via the Web Interface.  This script is run nightly on my NAS device to ensure that any new tracks which have been added to my Google Music Library will be downloaded and ready for adding to my local music library (which is served to my home network via [MiniDLNA](http://sourceforge.net/projects/minidlna/)).

## Installation
	pip install -r requirements.txt

## Usage
	# take a copy of the example settings file
	cp settings.example.json settings.json

	# Edit it to your liking
	vi settings.json

	# run the script - the first time it runs, nothing will be downloaded.
	python GoogleMusicSync.py