# -*- coding: utf-8 -*-

"""
Base class for unified handling of various archive formats. Used for simplifying
extraction and adding new archive formats
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from mcomix.constants import Constants


class BaseArchive:
    """
    Base archive interface.
    """

    def __init__(self, archive: Path):
        super().__init__()

        self.archive = archive

        if not Path.exists(Constants.PATHS['CACHE']):
            Constants.PATHS['CACHE'].mkdir(parents=True, exist_ok=True)

        self.__tempdir = TemporaryDirectory(dir=Constants.PATHS['CACHE'])

    @property
    def destdir(self):
        return self.__tempdir.name

    def iter_contents(self):
        """
        Generator for listing the archive contents
        """

        raise NotImplementedError

    def iter_extract(self, destination_dir: Path):
        """
        Generator to extract <wanted> from archive to <destination_dir>

        :param wanted: files to extract
        :param destination_dir: extraction path
        """

        raise NotImplementedError

    def close(self):
        """
        Closes the archive and releases held resources
        """

        logger.debug(f'Cleanup TemporaryDirectory: \'{self.__tempdir}\'')
        self.__tempdir.cleanup()

    def _create_directory(self, path: Path):
        """
        Recursively create a directory if it doesn't exist yet
        """

        if path.is_dir():
            return

        path.mkdir(parents=True, exist_ok=True)

    def _create_file(self, path: Path):
        """
        Open <dst_path> for writing, making sure base directory exists

        :returns: created image path
        """

        # recreate the archives directory structure,
        # needed for archives that are not flat
        self._create_directory(path.parent)

        return Path.open(path, mode='wb')
