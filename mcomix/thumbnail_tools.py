# -*- coding: utf-8 -*-

"""thumbnail.py - Thumbnail module for MComix implementing (most of) the
freedesktop.org "standard" at http://jens.triq.net/thumbnail-spec/"""

import os
import re
import threading

from loguru import logger

from mcomix import callback, image_tools, tools
from mcomix.preferences import prefs


class Thumbnailer:
    """The Thumbnailer class is responsible for managing MComix
    internal thumbnail creation. Depending on its settings,
    it either stores thumbnails on disk and retrieves them later,
    or simply creates new thumbnails each time it is called"""

    def __init__(self, size=None, archive_support=False):
        """<dst_dir> set the thumbnailer's storage directory.

        The dimensions for the created thumbnails is set by <size>, a (width,
        height) tupple. Defaults to the 'thumbnail size' preference if not set.

        If <archive_support> is True, support for archive thumbnail creation
        (based on cover detection) is enabled. Otherwise, only image files are
        supported"""
        if size is None:
            self.__width = self.__height = prefs['thumbnail size']
            self.__default_sizes = True
        else:
            self.__width, self.__height = size
            self.__default_sizes = False
        self.__archive_support = archive_support

    def thumbnail(self, filepath, mt=False):
        """Returns a thumbnail pixbuf for <filepath>, transparently handling
        both normal image files and archives. If a thumbnail file already exists,
        it is re-used. Otherwise, a new thumbnail is created from <filepath>.
        Returns None if thumbnail creation failed, or if the thumbnail creation
        is run asynchrounosly"""
        # Update width and height from preferences if they haven't been set explicitly
        if self.__default_sizes:
            self.__width = prefs['thumbnail size']
            self.__height = prefs['thumbnail size']

        if mt:
            thread = threading.Thread(target=self._create_thumbnail, args=(filepath,))
            thread.name += '-thumbnailer'
            thread.daemon = True
            thread.start()
            return None

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

    @staticmethod
    def _guess_cover(files):
        """Return the filename within <files> that is the most likely to be the
        cover of an archive using some simple heuristics"""
        # Ignore MacOSX meta files.
        files = filter(lambda filename:
                       '__MACOSX' not in os.path.normpath(filename).split(os.sep), files)
        # Ignore credit files if possible.
        files = filter(lambda filename:
                       'credit' not in os.path.split(filename)[1].lower(), files)

        images = [f for f in files if image_tools.is_image_file(f)]

        tools.alphanumeric_sort(images)

        front_re = re.compile('(cover|front)', re.I)
        candidates = filter(front_re.search, images)
        candidates = [c for c in candidates if 'back' not in c.lower()]

        if candidates:
            return candidates[0]

        if images:
            return images[0]

        return None
