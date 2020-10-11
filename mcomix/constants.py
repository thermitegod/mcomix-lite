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

        self.AXIS_DISTRIBUTION, self.AXIS_ALIGNMENT = self.AXIS_WIDTH, self.AXIS_HEIGHT = 0, 1
        self.SHOW_DOUBLE_NEVER, self.SHOW_DOUBLE_AS_ONE_TITLE, self.SHOW_DOUBLE_AS_ONE_WIDE = 0, 1, 2
        self.SORT_NONE, self.SORT_NAME, self.SORT_LOCALE, self.SORT_SIZE, self.SORT_LAST_MODIFIED, self.SORT_NAME_LITERAL = 0, 1, 2, 3, 4, 5
        self.SORT_DESCENDING, self.SORT_ASCENDING = 0, 1
        self.CURSOR_NORMAL, self.CURSOR_GRAB, self.CURSOR_WAIT, self.CURSOR_NONE = 0, 1, 2, 3
        self.AUTOROTATE_NEVER, self.AUTOROTATE_WIDTH_90, self.AUTOROTATE_WIDTH_270, self.AUTOROTATE_HEIGHT_90, self.AUTOROTATE_HEIGHT_270 = 0, 1, 2, 3, 4
        self.ZOOM_MODE_BEST, self.ZOOM_MODE_WIDTH, self.ZOOM_MODE_HEIGHT, self.ZOOM_MODE_MANUAL, self.ZOOM_MODE_SIZE = 0, 1, 2, 3, 4
        self.ZIP, self.RAR, self.SEVENZIP = 0, 1, 2

        self.SCROLL_TO_END, self.SCROLL_TO_START, self.SCROLL_TO_CENTER = -4, -3, -2
        self.INDEX_UNION, self.INDEX_LAST, self.INDEX_FIRST = -2, -1, 0
        self.ANIMATION_DISABLED, self.ANIMATION_NORMAL, self.ANIMATION_ONCE, self.ANIMATION_INF = 0, 1, 2, 3
        self.RESPONSE_REVERT_TO_DEFAULT, self.RESPONSE_REMOVE = 3, 4

        # These are bit field values, so only use powers of two.
        self.STATUS_PAGE, self.STATUS_RESOLUTION, self.STATUS_PATH, self.STATUS_FILENAME, self.STATUS_FILENUMBER, self.STATUS_FILESIZE, self.STATUS_MODE = 1, 2, 4, 8, 16, 32, 62

        self.ORIENTATION_MANGA, self.ORIENTATION_WESTERN = (-1, 1), (1, 1)

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
