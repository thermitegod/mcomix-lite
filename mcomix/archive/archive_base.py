# -*- coding: utf-8 -*-

"""
Base class for unified handling of various archive formats. Used for simplifying
extraction and adding new archive formats
"""

import threading
from pathlib import Path


class BaseArchive:
    """
    Base archive interface.
    """

    def __init__(self, archive):
        super().__init__()

        self.archive = archive

        self.lock = threading.Lock()

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
        :returns: full path of the extracted file
        """

        raise NotImplementedError

    def iter_extract(self, entries: set, destination_dir: Path):
        """
        Generator to extract <entries> from archive to <destination_dir>

        :param entries: files to extract
        :param destination_dir: extraction path
        """

        raise NotImplementedError

    def close(self):
        """
        Closes the archive and releases held resources
        """

        raise NotImplementedError

    @staticmethod
    def _create_file(dst_path: Path):
        """
        Open <dst_path> for writing, making sure base directory exists

        :returns: created image path
        """

        dst_dir = dst_path.parent

        # Create directory if it doesn't exist
        if not Path.exists(dst_dir):
            dst_dir.mkdir(parents=True, exist_ok=True)

        return Path.open(dst_path, mode='wb')
