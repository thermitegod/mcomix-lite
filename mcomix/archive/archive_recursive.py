# -*- coding: utf-8 -*-

"""Class for transparently handling an archive containing sub-archives"""

from pathlib import Path


class ArchiveRecursive:
    def __init__(self, archive):
        super().__init__()

        self.__archive = archive
        self.__archive_destination_dir = None

        self.__contents_listed = False
        self.__contents = []

    def _iter_contents(self, archive):
        root = Path() / self.__archive.destdir / 'main_archive'
        self.__archive_destination_dir = root

        for f in archive.iter_contents():
            yield str(Path(root, f))

    def iter_contents(self):
        """
        Generator for listing the archive contents
        """

        if self.__contents_listed:
            for f in self.__contents:
                yield f
            return

        self.__contents = []
        for f in self._iter_contents(archive=self.__archive):
            self.__contents.append(f)
            yield f

        self.__contents_listed = True

    def iter_extract(self):
        """
        extract archive and return an iter of archive contents
        """

        for f in self.__archive.iter_extract(self.__archive_destination_dir):
            yield str(f)

    def close(self):
        """
        Close the archive handle before cleanup temporary directory
        """

        self.__archive.close()
        self.__archive.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
