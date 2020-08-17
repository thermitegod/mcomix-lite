# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

"""constants.py - Miscellaneous constants"""

import os

from pathlib import Path

APPNAME = 'MComix-Lite'
VERSION = '3.0.0.dev0'

REQUIRED_PIL_VERSION = '6.0.0'

MAX_THREADS = 128

PROG_NAME = 'mcomix'
try:
    CONFIG_DIR = Path() / os.environ['XDG_CONFIG_HOME'] / f'{PROG_NAME}'
    DATA_DIR = Path() / os.environ['XDG_DATA_HOME'] / f'{PROG_NAME}'
    CACHE_DIR = Path() / os.environ['XDG_CACHE_HOME'] / f'{PROG_NAME}'
except KeyError:
    CONFIG_DIR = Path.home() / f'.config/{PROG_NAME}'
    DATA_DIR = Path.home() / f'.local/share/{PROG_NAME}'
    CACHE_DIR = Path() / f'/tmp/{PROG_NAME}'

PREFERENCE_PATH = Path() / CONFIG_DIR / 'preferences.conf'
KEYBINDINGS_PATH = Path() / CONFIG_DIR / 'keybindings.conf'
BOOKMARK_PATH = Path() / DATA_DIR / 'bookmarks.json'

AXIS_DISTRIBUTION, AXIS_ALIGNMENT = AXIS_WIDTH, AXIS_HEIGHT = 0, 1
SHOW_DOUBLE_NEVER, SHOW_DOUBLE_AS_ONE_TITLE, SHOW_DOUBLE_AS_ONE_WIDE = 0, 1, 2
SORT_NONE, SORT_NAME, SORT_SIZE, SORT_LAST_MODIFIED, SORT_NAME_LITERAL = 0, 1, 2, 3, 4
SORT_DESCENDING, SORT_ASCENDING = 0, 1
CURSOR_NORMAL, CURSOR_GRAB, CURSOR_WAIT, CURSOR_NONE = 0, 1, 2, 3
AUTOROTATE_NEVER, AUTOROTATE_WIDTH_90, AUTOROTATE_WIDTH_270, AUTOROTATE_HEIGHT_90, AUTOROTATE_HEIGHT_270 = 0, 1, 2, 3, 4
ZOOM_MODE_BEST, ZOOM_MODE_WIDTH, ZOOM_MODE_HEIGHT, ZOOM_MODE_MANUAL, ZOOM_MODE_SIZE = 0, 1, 2, 3, 4
ZIP, RAR, SEVENZIP = 0, 1, 2

SCROLL_TO_END, SCROLL_TO_START, SCROLL_TO_CENTER = -4, -3, -2
INDEX_UNION, INDEX_LAST, INDEX_FIRST = -2, -1, 0
ANIMATION_DISABLED, ANIMATION_NORMAL, ANIMATION_ONCE, ANIMATION_INF = 0, 1, 1 << 1, 1 << 2
RESPONSE_REVERT_TO_DEFAULT, RESPONSE_REMOVE = 3, 4

# These are bit field values, so only use powers of two.
STATUS_PAGE, STATUS_RESOLUTION, STATUS_PATH, STATUS_FILENAME, STATUS_FILENUMBER, STATUS_FILESIZE = 1, 2, 4, 8, 16, 32

ORIENTATION_MANGA, ORIENTATION_WESTERN = (-1, 1), (1, 1)

# see https://www.freedesktop.org/wiki/Software/shared-mime-info/
# for mimetypes not registed to IANA

ZIP_FORMATS = (
    ('.zip', 'application/zip'),
    ('.cbz', 'application/vnd.comicbook+zip'),
)

RAR_FORMATS = (
    ('.rar', 'application/vnd.rar'),
    ('.cbr', 'application/vnd.comicbook-rar'),
)

SZIP_FORMATS = (
    ('.7z', 'application/x-7z-compressed'),
    ('.cb7', 'application/x-cb7'),
)

ARCHIVE_DESCRIPTIONS = {
    ZIP: 'ZIP archive',
    SEVENZIP: '7z archive',
    RAR: 'RAR archive',
}
