# -*- coding: utf-8 -*-

import collections
import tarfile
from pathlib import Path

from loguru import logger

from mcomix.archive.archive_base import BaseArchive


class TarArchive(BaseArchive):
    def __init__(self, archive: Path):
        super().__init__(archive)

        self.__tar = tarfile.open(archive, mode='r')

        # tarfile is not thread-safe
        # so use OrderedDict to save TarInfo in order
        # {unicode_name: TarInfo}
        self.__contents_info = collections.OrderedDict()
        for member in self.__tar.getmembers():
            self.__contents_info[member.name] = member

    @staticmethod
    def is_available():
        return True

    def iter_contents(self):
        yield from self.__contents_info.keys()

    def extract(self, filename: str, destination_dir: Path):
        """
        Extract <filename> from the archive to <destination_dir>

        :param filename: file to extract
        :type filename: str
        :param destination_dir: extraction path
        :type destination_dir: Path
        :returns: full path of the extracted file
        :rtype: Path
        """

        with self.lock:
            info = self.__contents_info[filename]
            try:
                with self.__tar.extractfile(info) as fp:
                    data = fp.read()
            except AttributeError:
                logger.warning(f'Corrupted file: {filename}')

        destination_path = Path() / destination_dir / filename
        with self._create_file(destination_path) as new:
            new.write(data)

        return destination_path

    def close(self):
        self.__tar.close()
