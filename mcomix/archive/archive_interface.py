# -*- coding: utf-8 -*-

from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from mcomix.constants import Constants


class ArchiveInterface:
    def __init__(self, archive):
        super().__init__()

        self.__main_archive = archive

        if not Path.exists(Constants.PATHS['CACHE']):
            Constants.PATHS['CACHE'].mkdir(parents=True, exist_ok=True)

        self.__tempdir = TemporaryDirectory(dir=Constants.PATHS['CACHE'])
        self.__destdir = self.__tempdir.name
        # Map entry name to its archive+name.
        self.__entry_mapping = {}
        # Map archive to its root.
        self.__archive_destination_dir = None
        self.__contents_listed = False
        self.__contents = []

    def get_destdir(self):
        """
        Get the directry that the archive will be extracted to

        :return: path to extraction dir
        """

        return self.__destdir

    def _iter_contents(self):
        self.__archive_destination_dir = Path() / self.__destdir / 'main_archive'

        for f in self.__main_archive.iter_contents():
            name = str(Path(self.__archive_destination_dir, f))
            self.__entry_mapping[name] = f

            yield name

    def iter_contents(self):
        if self.__contents_listed:
            for f in self.__contents:
                yield f
            return

        self.__contents = []
        for f in self._iter_contents():
            self.__contents.append(f)
            yield f

        self.__contents_listed = True

    def iter_extract(self, entries: list):
        """
        List archive contents
        """

        archive_wanted = {}
        for name in entries:
            archive_wanted[self.__entry_mapping[name]] = name

        logger.debug(f'Extracting from {self.__main_archive.archive} to '
                     f'{self.__archive_destination_dir}: '
                     f'{" ".join(archive_wanted.keys())}')

        for f in self.__main_archive.iter_extract(set(archive_wanted.keys()), self.__archive_destination_dir):
            yield archive_wanted[f]

    def close(self):
        """
        Close the archive handle before cleanup temporary directory
        """

        self.__main_archive.close()
        self.__tempdir.cleanup()
