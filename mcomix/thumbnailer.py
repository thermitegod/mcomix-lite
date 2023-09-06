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

from pathlib import Path

from PIL import Image
from loguru import logger

from mcomix.image_tools import ImageTools
from mcomix.lib.reader import LockedFileIO


class Thumbnailer:
    def __init__(self):
        """
        The Thumbnailer class is responsible for thumbnail creation.

        :param size: The dimensions for the created thumbnails (width, height).
        """

        super().__init__()

    def __call__(self, size: tuple, filepath: Path):
        """
        Returns a thumbnail pixbuf for <filepath>, transparently handling
        both normal image files and archives. Returns None if thumbnail creation
        failed, or if the thumbnail creation is run asynchrounosly

        :param size: The dimensions for the created thumbnails (width, height).
        :param filepath: Path to the image that the thumbnail is generated from.
        """

        try:
            with LockedFileIO(filepath) as fio:
                with Image.open(fio) as im:
                    im.thumbnail(size, resample=Image.BOX)
                    im = ImageTools.add_border_pil(im)
                    pixbuf = ImageTools.pil_to_pixbuf(im)
                    if ImageTools.pil_has_alpha(im):
                        pixbuf = ImageTools.add_alpha_background(pixbuf, pixbuf.get_width(), pixbuf.get_height())
        except Exception as ex:
            logger.error(f'Failed to create thumbnail for image: \'{filepath}\'')
            logger.error(f'Exception: {ex}')
            pixbuf = None

        return pixbuf
