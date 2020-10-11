# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

"""constants.py - Miscellaneous constants"""

import os
from pathlib import Path

from loguru import logger


class _Constants:
    def __init__(self):
        self.APPNAME = 'MComix-Lite'
        self.VERSION = '3.1.0.dev0'

        self.REQUIRED_PIL_VERSION = '6.0.0'

        self.MAX_THREADS = 128

        self.PROG_NAME = self.APPNAME.lower()
        try:
            self.CONFIG_DIR = Path() / os.environ['XDG_CONFIG_HOME'] / self.PROG_NAME
            self.DATA_DIR = Path() / os.environ['XDG_DATA_HOME'] / self.PROG_NAME
            self.CACHE_DIR = Path() / os.environ['XDG_CACHE_HOME'] / self.PROG_NAME
        except KeyError:
            logger.warning('Not using XDG dirs, falling back to hardcoded paths')
            self.CONFIG_DIR = Path.home() / '.config' / self.PROG_NAME
            self.DATA_DIR = Path.home() / '.local/share' / self.PROG_NAME
            self.CACHE_DIR = Path() / '/tmp' / self.PROG_NAME

        self.PREFERENCE_PATH = Path() / self.CONFIG_DIR / 'preferences.conf'
        self.KEYBINDINGS_PATH = Path() / self.CONFIG_DIR / 'keybindings.conf'
        self.BOOKMARK_PATH = Path() / self.DATA_DIR / 'bookmarks.json'

        self.AXIS_DISTRIBUTION = 0
        self.AXIS_ALIGNMENT = 1

        self.AXIS_WIDTH = 0
        self.AXIS_HEIGHT = 1

        self.SHOW_DOUBLE_NEVER = 0
        self.SHOW_DOUBLE_AS_ONE_TITLE = 1
        self.SHOW_DOUBLE_AS_ONE_WIDE = 2

        self.SORT_NONE = 0
        self.SORT_NAME = 1
        self.SORT_LOCALE = 2
        self.SORT_SIZE = 3
        self.SORT_LAST_MODIFIED = 4
        self.SORT_NAME_LITERAL = 5

        self.SORT_DESCENDING = 0
        self.SORT_ASCENDING = 1

        self.CURSOR_NORMAL = 0
        self.CURSOR_GRAB = 1
        self.CURSOR_WAIT = 2
        self.CURSOR_NONE = 3

        self.AUTOROTATE_NEVER = 0
        self.AUTOROTATE_WIDTH_90 = 1
        self.AUTOROTATE_WIDTH_270 = 2
        self.AUTOROTATE_HEIGHT_90 = 3
        self.AUTOROTATE_HEIGHT_270 = 4

        self.ZOOM_MODE_BEST = 0
        self.ZOOM_MODE_WIDTH = 1
        self.ZOOM_MODE_HEIGHT = 2
        self.ZOOM_MODE_MANUAL = 3
        self.ZOOM_MODE_SIZE = 4

        self.ZIP = 0
        self.SEVENZIP = 1
        self.RAR = 2

        # Constants for determining which files to list.
        self.IMAGES = 1
        self.ARCHIVES = 2

        self.SCROLL_TO_END = -4
        self.SCROLL_TO_START = -3
        self.SCROLL_TO_CENTER = -2

        self.INDEX_UNION = -2
        self.INDEX_LAST = -1
        self.INDEX_FIRST = 0

        self.ANIMATION_DISABLED = 0
        self.ANIMATION_NORMAL = 1
        self.ANIMATION_ONCE = 2
        self.ANIMATION_INF = 3

        self.RESPONSE_REVERT_TO_DEFAULT = 3
        self.RESPONSE_REMOVE = 4

        # These are bit field values, so only use powers of two.
        self.STATUS_PAGE = 1
        self.STATUS_RESOLUTION = 2
        self.STATUS_PATH = 4
        self.STATUS_FILENAME = 8
        self.STATUS_FILENUMBER = 16
        self.STATUS_FILESIZE = 32
        self.STATUS_MODE = 62

        self.ORIENTATION_MANGA = (-1, 1)
        self.ORIENTATION_WESTERN = (1, 1)

        # see https://www.freedesktop.org/wiki/Software/shared-mime-info/
        # for mimetypes not registed to IANA

        self.ZIP_FORMATS = (
            ('.zip', 'application/zip'),
            ('.cbz', 'application/vnd.comicbook+zip'),
        )

        self.RAR_FORMATS = (
            ('.rar', 'application/vnd.rar'),
            ('.cbr', 'application/vnd.comicbook-rar'),
        )

        self.SZIP_FORMATS = (
            ('.7z', 'application/x-7z-compressed'),
            ('.cb7', 'application/x-cb7'),
        )

        self.ARCHIVE_DESCRIPTIONS = {
            self.ZIP: 'ZIP archive',
            self.SEVENZIP: '7z archive',
            self.RAR: 'RAR archive',
        }


Constants = _Constants()
