# -*- coding: utf-8 -*-

"""
Base class for unified handling of various archive formats. Used for simplifying
extraction and adding new archive formats
"""

from pathlib import Path

from mcomix.archive.archive_base import BaseArchive


class ArchiveBuiltin(BaseArchive):
    def __init__(self, archive):
        super().__init__(archive)

        self.contents_info = {}

    @staticmethod
    def is_available():
        return True

    def iter_contents(self):
        """
        Generator for listing the archive contents
        """

        yield from self.contents_info.keys()

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

    def iter_extract(self, wanted: set, destination_dir: Path):
        """
        Generator to extract <wanted> from archive to <destination_dir>

        :param wanted: files to extract
        :param destination_dir: extraction path
        """

        for filename in self.iter_contents():
            if filename not in wanted:
                continue
            self.extract(filename, destination_dir)
            yield filename
            wanted.remove(filename)
            if not wanted:
                break

    def close(self):
        """
        Closes the archive and releases held resources
        """

        raise NotImplementedError
