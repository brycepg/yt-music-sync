#!/usr/bin/env python3

import argparse
import datetime
import logging
import os

from youtube_dl import YoutubeDL

__author__ = "Bryce Guinta"
__version__ = "1.0"
__license__ = "MIT"

log = logging.getLogger(__name__)


def main():
    # type: () -> None
    """Main entry point for the cli-interface."""
    setup_logging()
    vargs = parse_args()
    run(**vargs)


def parse_args():
    # type: () -> dict[str, Any]
    parser = argparse.ArgumentParser(
        "Sync mp3s from a youtube playlist the given directory. "
        "Checks the given directory for existing mp3s from the playlist "
        "before downloading to reduce bandwidth/time.")
    parser.add_argument("url", help="Url to youtube playlist.")
    parser.add_argument("--path", default="", help="Path to store results")
    parser.add_argument("--verbose", action="store_true", default=False)
    args = parser.parse_args()
    vargs = vars(args)
    return vargs


def setup_logging():
    # type: () -> None
    """Setup logging for cli-interface.

    Set everything to debug by default.
    Add a stream handler for stdout to the current module."""
    logging.getLogger().setLevel(logging.DEBUG)
    fmt = MyFormatter("[%(asctime)s]: %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(fmt)
    handler.setLevel(logging.DEBUG)
    log.setLevel(logging.DEBUG)
    log.handlers = []
    log.addHandler(handler)


def run(url, verbose=False, path=""):
    # type: (str, bool, str) -> None
    """API interface to this utility.

    args:
        url: Url to playlist to download
        verbose: If True set logger level to DEUBG, otherwise INFO
        path: Path to download/comparison directory. Defaults to
            current directory.

    """

    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    log.info("Downloading playlist json.")
    with CD(path):
        dl_url_list = get_missing_entries(url)
        download_url_list(dl_url_list)


def download_url_list(dl_url_list):
    # type: (List[str]) -> None
    """Setup YoutubeDL object and download sources list."""
    yt_dl = YoutubeDL(
        {'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredquality': '0',
                'nopostoverwrites': False,
                'preferredcodec': 'mp3'
            },
        ],
            'outtmpl': '%(title)s.%(ext)s',
            'logger': YTLogger(),
        }
    )

    if dl_url_list:
        log.info("Starting download of %s entries", len(dl_url_list))
        yt_dl.download(dl_url_list)
        log.info("Ended download")
    else:
        log.info("There were no new entries found.")


def get_missing_entries(playlist_url):
    """Get json from playlist to determine which videos to download."""
    # type: () -> List[str]
    json_dl = YoutubeDL(
        {'force_json': True,
         'quiet': True,
         'simulate': True,
         'logger': YTLogger(),
         })
    ret_dict = json_dl.extract_info(playlist_url)
    missing_entries = yield_missing_files(ret_dict['entries'])
    dl_url_list = [entry['webpage_url'] for entry in missing_entries]
    return dl_url_list


def yield_missing_files(entry_list):
    # type: (Iterable[dict]) -> Iterable[dict]
    """Filter dictionaries that already correspond to a file.

    Makes the assumption that the downloaded template was %(title)s.mp3

    Args:
        entry_list: A list of entries that correspond to videos on youtube.
        Must have a 'title' key.

    Yields:
        Entries that do not have a mp3 file named after them.
    """
    for elem in entry_list:
        path = "{name}.{ext}".format(name=elem['title'], ext='mp3')
        if not os.path.exists(path):
            yield elem
        else:
            log.debug("'%s' already exists", elem['title'])


class YTLogger(object):
    """Logger for youtube_dl.

    Supresses stdout noise.
    """
    def debug(self, msg):
        log.debug(msg)

    def warning(self, msg):
        log.warning(msg)

    def error(self, msg):
        log.error(msg)


class MyFormatter(logging.Formatter):
    """Add format for hours, minutes, seconds and milliseconds"""
    def formatTime(self, record, *args):
        ct = datetime.datetime.fromtimestamp(record.created)
        t = ct.strftime("%H:%M:%S")
        s = "%s,%03d" % (t, record.msecs)
        return s


class CD(object):
    """Context manager for changing the current working directory."""
    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        self.saved_path = os.getcwd()
        if self.new_path:
            os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        if self.new_path:
            os.chdir(self.saved_path)


if __name__ == "__main__":
    main()
