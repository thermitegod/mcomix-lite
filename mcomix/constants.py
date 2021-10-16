# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

"""constants.py - Miscellaneous constants"""

from collections import namedtuple

import PIL.Image
from gi.repository import GdkPixbuf


class _Constants:
    def __init__(self):
        super().__init__()

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
