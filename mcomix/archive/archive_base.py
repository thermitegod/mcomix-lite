# -*- coding: utf-8 -*-

"""
Base class for unified handling of various archive formats. Used for simplifying
extraction and adding new archive formats
"""

from pathlib import Path

from mcomix.lib.threadpool import Lock


class BaseArchive:
    """
    Base archive interface.
    """

    def __init__(self, archive):
        super().__init__()

        self.archive = archive

        self.lock = Lock()

    def iter_contents(self):
        """
        Generator for listing the archive contents
        """

        raise NotImplementedError

    def extract(self, filename: str, destination_dir: Path):
        """
        Extracts the file specified by <filename> and return the path of it.
        This filename must be obtained by calling list_contents().
        The file is saved to <destination_dir>

        :param filename: file to extract
        :param destination_dir: extraction path
        """

        raise NotImplementedError

    def iter_extract(self, wanted: set, destination_dir: Path):
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

        raise NotImplementedError

    @staticmethod
    def _create_file(path: Path):
        """
        Open <dst_path> for writing, making sure base directory exists

        :returns: created image path
        """

        # recreate the archives directory structure,
        # needed for archives that are not flat
        dst_dir = path.parent
        if not dst_dir.is_dir():
            dst_dir.mkdir(parents=True, exist_ok=True)

        return Path.open(path, mode='wb')
