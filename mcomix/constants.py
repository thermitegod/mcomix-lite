# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

"""constants.py - Miscellaneous constants"""

import os
from collections import namedtuple
from pathlib import Path

import PIL.Image
from gi.repository import GdkPixbuf
from loguru import logger


class _Constants:
    def __init__(self):
        super().__init__()

        self.APPNAME = 'MComix-Lite'
        self.VERSION = '3.2.0'

        self.PROG_NAME = self.APPNAME.lower()
        self.HOME = Path.home()
        try:
            self.PATHS = {
                'CONFIG': Path() / os.environ['XDG_CONFIG_HOME'] / self.PROG_NAME,
                'DATA': Path() / os.environ['XDG_DATA_HOME'] / self.PROG_NAME,
                'CACHE': Path() / os.environ['XDG_CACHE_HOME'] / self.PROG_NAME,
            }
        except KeyError:
            logger.warning('Not using XDG dirs, falling back to hardcoded paths')
            self.PATHS = {
                'CONFIG': self.HOME / '.config' / self.PROG_NAME,
                'DATA': self.HOME / '.local/share' / self.PROG_NAME,
                'CACHE': Path() / '/tmp' / self.PROG_NAME,
            }

        self.CONFIG_FILES = {
            'CONFIG': self.PATHS['CONFIG'] / 'mcomix.conf',
            'KEYBINDINGS': self.PATHS['CONFIG'] / 'input.conf',
            'BOOKMARK': self.PATHS['DATA'] / 'bookmarks.yml',
        }

        self.AXIS = {
            'DISTRIBUTION': 0,
            'ALIGNMENT': 1,
            'WIDTH': 0,
            'HEIGHT': 1,
        }

        self.DOUBLE_PAGE = {
            'NEVER': 0,
            'AS_ONE_TITLE': 1,
            'AS_ONE_WIDE': 2,
        }

        self.FILE_SORT_TYPE = {
            'NONE': 0,
            'NAME': 1,
            'SIZE': 2,
            'LAST_MODIFIED': 3,
            'NAME_LITERAL': 4,
        }

        self.FILE_SORT_DIRECTION = {
            'DESCENDING': 0,
            'ASCENDING': 1,
        }

        self.CURSOR = {
            'NORMAL': 0,
            'GRAB': 1,
            'WAIT': 2,
            'NONE': 3,
        }

        self.AUTOROTATE = {
            'NEVER': 0,
            'WIDTH_90': 1,
            'WIDTH_270': 2,
            'HEIGHT_90': 3,
            'HEIGHT_270': 4,
        }

        self.ZOOM = {
            'BEST': 0,
            'WIDTH': 1,
            'HEIGHT': 2,
            'MANUAL': 3,
            'SIZE': 4,
        }

        self.ARCHIVE_FORMATS = {
            'ZIP': 0,
            'SEVENZIP': 1,
            'RAR': 2,
            'TAR': 3,
        }

        # Constants for determining which files to list.
        self.FILE_TYPE = {
            'IMAGES': 1,
            'ARCHIVES': 2,
        }

        self.SCROLL_TO = {
            'END': -4,
            'START': -3,
            'CENTER': -2,
        }

        self.ANIMATION = {
            'DISABLED': 0,
            'NORMAL': 1,
            'ONCE': 2,
            'INF': 3,
        }

        self.RESPONSE = {
            'REVERT_TO_DEFAULT': 3,
            'REMOVE': 4,
        }

        self.ORIENTATION = {
            'MANGA': [-1, 1],
            'WESTERN': [1, 1],
        }

        SCALING = namedtuple('SCALING', ['name', 'value'])
        self.SCALING_GDK = (
            SCALING('Nearest', int(GdkPixbuf.InterpType.NEAREST)),
            SCALING('Tiles', int(GdkPixbuf.InterpType.TILES)),
            SCALING('Bilinear', int(GdkPixbuf.InterpType.BILINEAR)),
        )

        self.SCALING_PIL = (
            SCALING('Nearest', PIL.Image.NEAREST),
            SCALING('Lanczos', PIL.Image.LANCZOS),
            SCALING('Bilinear', PIL.Image.BILINEAR),
            SCALING('Bicubic', PIL.Image.BICUBIC),
            SCALING('Box', PIL.Image.BOX),
            SCALING('Hamming', PIL.Image.HAMMING),
        )

        # see https://www.freedesktop.org/wiki/Software/shared-mime-info/
        # for mimetypes not registed to IANA

        self.MIME_FORMAT = {
            'ZIP': (
                ('.zip', 'application/zip'),
                ('.cbz', 'application/vnd.comicbook+zip'),
            ),

            'RAR': (
                ('.rar', 'application/vnd.rar'),
                ('.cbr', 'application/vnd.comicbook-rar'),
            ),

            'SEVENZIP': (
                ('.7z', 'application/x-7z-compressed'),
                ('.cb7', 'application/x-cb7'),
            ),

            'TAR': (
                ('.tar', 'application/x-tar'),
                ('.cbt', 'application/x-cbt'),
                # compressed tar
                ('.gz', 'application/x-compressed-tar'),
                ('.bz2', 'application/x-bzip-compressed-tar'),
                ('.lzma', 'application/x-lzma-compressed-tar'),
                ('.xz', 'application/x-xz-compressed-tar'),
            ),
        }

        self.ARCHIVE_DESCRIPTIONS = {
            self.ARCHIVE_FORMATS['ZIP']: 'ZIP archive',
            self.ARCHIVE_FORMATS['SEVENZIP']: '7z archive',
            self.ARCHIVE_FORMATS['RAR']: 'RAR archive',
            self.ARCHIVE_FORMATS['TAR']: 'TAR archive',
        }


Constants = _Constants()
