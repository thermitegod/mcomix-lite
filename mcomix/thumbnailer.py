# -*- coding: utf-8 -*-

from pathlib import Path

from PIL import Image
from loguru import logger

from mcomix.image_tools import ImageTools
from mcomix.lib.reader import LockedFileIO


class Thumbnailer:
    def __init__(self, size: tuple):
        """
        The Thumbnailer class is responsible for thumbnail creation.

        :param size: The dimensions for the created thumbnails (width, height).
        """

        super().__init__()

        self.__width, self.__height = size

    def thumbnail(self, filepath: Path):
        """
        Returns a thumbnail pixbuf for <filepath>, transparently handling
        both normal image files and archives. Returns None if thumbnail creation
        failed, or if the thumbnail creation is run asynchrounosly
        """

        # any exceptions get handled by caller

        with LockedFileIO(filepath) as fio:
            with Image.open(fio) as im:
                im.thumbnail((self.__width, self.__height), resample=Image.BOX)
                return ImageTools.pil_to_pixbuf(im)
