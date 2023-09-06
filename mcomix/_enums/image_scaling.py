from enum import Enum

import PIL.Image
from gi.repository import GdkPixbuf


class ScalingGDK(Enum):
    Nearest = int(GdkPixbuf.InterpType.NEAREST)
    Tiles = int(GdkPixbuf.InterpType.TILES)
    Bilinear = int(GdkPixbuf.InterpType.BILINEAR)


class ScalingPIL(Enum):
    Nearest = PIL.Image.NEAREST
    Lanczos = PIL.Image.LANCZOS
    Bilinear = PIL.Image.BILINEAR
    Bicubic = PIL.Image.BICUBIC
    Box = PIL.Image.BOX
    Hamming = PIL.Image.HAMMING
