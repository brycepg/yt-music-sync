Overview
########

This script is for 'syncing' a YouTube music playlist with a directory.

Use the ``--path`` argument to specify the path to the desired location to download
and check for existing files. Defaults to the current directory.

Give the url of the playlist as a positional argument.

I created this to reduce the download time and bandwidth required to sync a playlist
with a directory since I only download what is missing.

Also since I run this as a cronjob, allowing to specify the download path as an argument comes in handy


Requirements
############

Requires:

- youtube-dl
- ffmpeg
- libmp3lame codec

Arguments
#########

    usage: Sync mp3s from a youtube playlist the given directory. Checks the given directory for existing mp3s from the playlist before downloading to reduce bandwidth/time.
           [-h] [--path PATH] [--verbose] url

    positional arguments:
      url          Url to youtube playlist.

    optional arguments:
      -h, --help   show this help message and exit
      --path PATH  Path to store results
      --verbose
