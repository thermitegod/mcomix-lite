# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

"""constants.py - Miscellaneous constants"""

import os

from pathlib import Path

APPNAME = 'MComix-Lite'
VERSION = '3.0.0-dev'

REQUIRED_PIL_VERSION = '6.0.0'

MAX_THREADS = 128

try:
    CONFIG_DIR = Path() / os.environ['XDG_CONFIG_HOME'] / 'mcomix'
    DATA_DIR = Path() / os.environ['XDG_DATA_HOME'] / 'mcomix'
except KeyError:
    CONFIG_DIR = Path.home() / '.config/mcomix'
    DATA_DIR = Path.home() / '.local/share/mcomix'

PREFERENCE_PATH = Path() / CONFIG_DIR / 'preferences.conf'
KEYBINDINGS_PATH = Path() / CONFIG_DIR / 'keybindings.conf'
BOOKMARK_PATH = Path() / DATA_DIR / 'bookmarks.json'

DISTRIBUTION_AXIS, ALIGNMENT_AXIS = WIDTH_AXIS, HEIGHT_AXIS = 0, 1
SHOW_DOUBLE_NEVER, SHOW_DOUBLE_AS_ONE_TITLE, SHOW_DOUBLE_AS_ONE_WIDE = 0, 1, 2
SORT_NONE, SORT_NAME, SORT_SIZE, SORT_LAST_MODIFIED, SORT_NAME_LITERAL = 0, 1, 2, 3, 4
SORT_DESCENDING, SORT_ASCENDING = 0, 1
NORMAL_CURSOR, GRAB_CURSOR, WAIT_CURSOR, NO_CURSOR = 0, 1, 2, 3
AUTOROTATE_NEVER, AUTOROTATE_WIDTH_90, AUTOROTATE_WIDTH_270, AUTOROTATE_HEIGHT_90, AUTOROTATE_HEIGHT_270 = 0, 1, 2, 3, 4
ZOOM_MODE_BEST, ZOOM_MODE_WIDTH, ZOOM_MODE_HEIGHT, ZOOM_MODE_MANUAL, ZOOM_MODE_SIZE = 0, 1, 2, 3, 4
ZIP, RAR, SEVENZIP = 0, 1, 2

# These are bit field values, so only use powers of two.
STATUS_PAGE, STATUS_RESOLUTION, STATUS_PATH, STATUS_FILENAME, STATUS_FILENUMBER, STATUS_FILESIZE = 1, 2, 4, 8, 16, 32

WESTERN_ORIENTATION = (1, 1)
MANGA_ORIENTATION = (-1, 1)
SCROLL_TO_CENTER = -2
SCROLL_TO_START = -3
SCROLL_TO_END = -4
FIRST_INDEX = 0
LAST_INDEX = -1
UNION_INDEX = -2
ANIMATION_DISABLED = 0
ANIMATION_NORMAL = 1  # loop as animation setting
ANIMATION_ONCE = 1 << 1  # loop only once
ANIMATION_INF = 1 << 2  # loop infinity
RESPONSE_REVERT_TO_DEFAULT = 3
RESPONSE_REMOVE = 4

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
