# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

"""constants.py - Miscellaneous constants"""

import os

APPNAME = 'MComix-Lite'
VERSION = '0.0.0'

REQUIRED_PIL_VERSION = '6.0.0'

CPU_COUNT = os.cpu_count()

HOME_DIR = os.environ.get('HOME')
CONFIG_DIR = os.path.join(os.getenv('XDG_CONFIG_HOME', os.path.join(HOME_DIR, '.config')), 'mcomix')
DATA_DIR = os.path.join(os.getenv('XDG_DATA_HOME', os.path.join(HOME_DIR, '.local/share')), 'mcomix')

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
THUMBNAIL_PATH = os.getenv('XDG_CACHE_HOME', os.path.join(HOME_DIR, '.cache/thumbnails/normal'))
PREFERENCE_PATH = os.path.join(CONFIG_DIR, 'preferences.conf')
KEYBINDINGS_CONF_PATH = os.path.join(CONFIG_DIR, 'keybindings.conf')

BOOKMARK_PATH = os.path.join(DATA_DIR, 'bookmarks.pickle')

ZOOM_MODE_BEST, ZOOM_MODE_WIDTH, ZOOM_MODE_HEIGHT, ZOOM_MODE_MANUAL, ZOOM_MODE_SIZE = range(5)

WIDTH_AXIS, HEIGHT_AXIS = range(2)
DISTRIBUTION_AXIS, ALIGNMENT_AXIS = WIDTH_AXIS, HEIGHT_AXIS
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

ZIP, RAR, PDF, SEVENZIP, LHA, ZIP_EXTERNAL = range(6)
NORMAL_CURSOR, GRAB_CURSOR, WAIT_CURSOR, NO_CURSOR = range(4)
AUTOROTATE_NEVER, AUTOROTATE_WIDTH_90, AUTOROTATE_WIDTH_270, AUTOROTATE_HEIGHT_90, AUTOROTATE_HEIGHT_270 = range(5)

RESPONSE_REVERT_TO_DEFAULT = 3
RESPONSE_REMOVE = 4

# These are bit field values, so only use powers of two.
STATUS_PAGE, STATUS_RESOLUTION, STATUS_PATH, STATUS_FILENAME, STATUS_FILENUMBER, STATUS_FILESIZE = 1, 2, 4, 8, 16, 32
SHOW_DOUBLE_AS_ONE_TITLE, SHOW_DOUBLE_AS_ONE_WIDE = 1, 2

SORT_NAME, SORT_SIZE, SORT_LAST_MODIFIED, SORT_NAME_LITERAL = 1, 2, 3, 4
SORT_DESCENDING, SORT_ASCENDING = 1, 2

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

LHA_FORMATS = (
    ('.lha', 'application/x-lha'),
    ('.lzh', 'application/x-lha'),
)

PDF_FORMATS = (
    ('.pdf', 'application/pdf'),
)

ARCHIVE_DESCRIPTIONS = {
    ZIP: 'ZIP archive',
    RAR: 'RAR archive',
    PDF: 'PDF document',
    SEVENZIP: '7z archive',
    LHA: 'LHA archive',
    ZIP_EXTERNAL: 'ZIP archive',
}
