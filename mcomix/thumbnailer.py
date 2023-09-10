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

from gi.repository import GdkPixbuf

from loguru import logger

import mcomix.image_tools as image_tools

class Thumbnailer:
    def __init__(self):
        """
        The Thumbnailer class is responsible for thumbnail creation.

        :param size: The dimensions for the created thumbnails (width, height).
        """

        super().__init__()

    def __call__(self, size: int, filepath: Path):
        """
        Returns a thumbnail pixbuf for <filepath>, transparently handling
        both normal image files and archives. Returns None if thumbnail creation
        failed, or if the thumbnail creation is run asynchrounosly

        :param size: The max size of any one side for the created thumbnails.
        :param filepath: Path to the image that the thumbnail is generated from.
        """

        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(filepath))
        except Exception as ex:
            logger.error(f'Failed to create thumbnail for image: \'{filepath}\'')
            logger.error(f'Exception: {ex}')
            return None

        original_width = pixbuf.get_width()
        original_height = pixbuf.get_height()

        # Calculate the new dimensions while preserving the aspect ratio
        aspect_ratio = original_width / original_height
        if original_width > original_height:
            width = size
            height = int(size / aspect_ratio)
        else:
            height = size
            width = int(size * aspect_ratio)

        pixbuf = image_tools.fit_pixbuf_to_rectangle(pixbuf, width, height, 0)
        pixbuf = image_tools.add_border_pixbuf(pixbuf)

        return pixbuf
