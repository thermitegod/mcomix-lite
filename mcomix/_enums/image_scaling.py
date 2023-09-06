# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

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
