# -*- coding: utf-8 -*-

"""thumbnail.py - Thumbnail module for MComix implementing (most of) the
freedesktop.org "standard" at http://jens.triq.net/thumbnail-spec/"""

from pathlib import Path

from mcomix.image_tools import ImageTools
from mcomix.lib.callback import Callback
from mcomix.preferences import config


class Thumbnailer:
    """
    The Thumbnailer class is responsible for managing MComix
    internal thumbnail creation. Depending on its settings,
    it either stores thumbnails on disk and retrieves them later,
    or simply creates new thumbnails each time it is called
    """

    def __init__(self, size: tuple = None):
        """
        <dst_dir> set the thumbnailer's storage directory.

        The dimensions for the created thumbnails is set by <size>, a (width,
        height) tupple. Defaults to the 'THUMBNAIL_SIZE' preference if not set.
        """

        super().__init__()

        if size is None:
            self.__width = self.__height = config['THUMBNAIL_SIZE']
            self.__default_sizes = True
        else:
            self.__width, self.__height = size
            self.__default_sizes = False

    def thumbnail(self, filepath: str):
        """
        Returns a thumbnail pixbuf for <filepath>, transparently handling
        both normal image files and archives. If a thumbnail file already exists,
        it is re-used. Otherwise, a new thumbnail is created from <filepath>.
        Returns None if thumbnail creation failed, or if the thumbnail creation
        is run asynchrounosly
        """

        # Update width and height from preferences if they haven't been set explicitly
        if self.__default_sizes:
            self.__width = config['THUMBNAIL_SIZE']
            self.__height = config['THUMBNAIL_SIZE']

        return self._create_thumbnail(Path(filepath))

    @Callback
    def thumbnail_finished(self, filepath: Path, pixbuf):
        """
        Called every time a thumbnail has been completed.
        <filepath> is the file that was used as source, <pixbuf> is the
        resulting thumbnail
        """

        pass

    def _create_thumbnail_pixbuf(self, filepath: Path):
        """
        Creates a thumbnail pixbuf from <filepath>, and returns it as a
        tuple: (pixbuf)
        """

        if ImageTools.is_image_file(filepath, check_mimetype=True):
            pixbuf = ImageTools.load_pixbuf_size(filepath, self.__width, self.__height)
            return pixbuf

        return None, None

    def _create_thumbnail(self, filepath: Path):
        """
        Creates the thumbnail pixbuf for <filepath>

        :returns: the created pixbuf, or None, if creation failed
        """

        pixbuf = self._create_thumbnail_pixbuf(filepath)
        self.thumbnail_finished(filepath, pixbuf)

        return pixbuf
