# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

"""constants.py - Miscellaneous constants"""

from collections import namedtuple

import PIL.Image
from gi.repository import GdkPixbuf


class _Constants:
    def __init__(self):
        super().__init__()

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


Constants = _Constants()
