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
from pathlib import Path

from PIL import Image


# disable PIL DecompressionBombWarning
Image.MAX_IMAGE_PIXELS = None

# formats supported by PIL
Image.init()


class ImageSupported(Enum):
    # formats supported by PIL
    EXTS = set([ext for ext in Image.EXTENSION
                if ext not in ('.pdf',)])

    @classmethod
    def is_image_file(cls, path: Path):
        return path.suffix.lower() in cls.EXTS.value
