# -*- coding: utf-8 -*-

"""thumbnail.py - Thumbnail module for MComix implementing (most of) the
freedesktop.org "standard" at http://jens.triq.net/thumbnail-spec/"""

from mcomix import image_tools
from mcomix.lib import callback
from mcomix.preferences import prefs


class Thumbnailer:
    """The Thumbnailer class is responsible for managing MComix
    internal thumbnail creation. Depending on its settings,
    it either stores thumbnails on disk and retrieves them later,
    or simply creates new thumbnails each time it is called"""

    def __init__(self, size=None):
        """<dst_dir> set the thumbnailer's storage directory.

        The dimensions for the created thumbnails is set by <size>, a (width,
        height) tupple. Defaults to the 'thumbnail size' preference if not set."""
        if size is None:
            self.__width = self.__height = prefs['thumbnail size']
            self.__default_sizes = True
        else:
            self.__width, self.__height = size
            self.__default_sizes = False

    def thumbnail(self, filepath):
        """Returns a thumbnail pixbuf for <filepath>, transparently handling
        both normal image files and archives. If a thumbnail file already exists,
        it is re-used. Otherwise, a new thumbnail is created from <filepath>.
        Returns None if thumbnail creation failed, or if the thumbnail creation
        is run asynchrounosly"""
        # Update width and height from preferences if they haven't been set explicitly
        if self.__default_sizes:
            self.__width = prefs['thumbnail size']
            self.__height = prefs['thumbnail size']

        return self._create_thumbnail(filepath)

    @callback.Callback
    def thumbnail_finished(self, filepath, pixbuf):
        """Called every time a thumbnail has been completed.
        <filepath> is the file that was used as source, <pixbuf> is the
        resulting thumbnail"""
        pass

    def _create_thumbnail_pixbuf(self, filepath):
        """Creates a thumbnail pixbuf from <filepath>, and returns it as a
        tuple: (pixbuf)"""
        if image_tools.is_image_file(filepath, check_mimetype=True):
            pixbuf = image_tools.load_pixbuf_size(filepath, self.__width, self.__height)
            return pixbuf

        return None, None

    def _create_thumbnail(self, filepath):
        """Creates the thumbnail pixbuf for <filepath>
        Returns the created pixbuf, or None, if creation failed"""
        pixbuf = self._create_thumbnail_pixbuf(filepath)
        self.thumbnail_finished(filepath, pixbuf)

        return pixbuf
