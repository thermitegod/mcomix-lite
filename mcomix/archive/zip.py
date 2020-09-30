# -*- coding: utf-8 -*-

"""Unicode-aware wrapper for zipfile.ZipFile"""

import collections
import threading
import zipfile
from pathlib import Path

from loguru import logger

from mcomix.archive.archive_base import BaseArchive


class ZipArchive(BaseArchive):
    def __init__(self, archive: str):
        super().__init__(archive)
        self.__zip = zipfile.ZipFile(archive, 'r')
        self.__lock = threading.Lock()

        # zipfile is usually not thread-safe
        # so use OrderedDict to save ZipInfo in order
        # {unicode_name: ZipInfo}
        self.__contents_info = collections.OrderedDict()
        for info in self.__zip.infolist():
            self.__contents_info[info.filename] = info

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

        with self.__lock:
            info = self.__contents_info[filename]
            data = self.__zip.read(info)

        destination_path = Path() / destination_dir / filename
        with self._create_file(destination_path) as new:
            filelen = new.write(data)

        if filelen != info.file_size:
            logger.warning(f'{filename}: extracted size is {filelen} bytes, but should be {info.file_size} bytes')

        return destination_path

    def close(self):
        self.__zip.close()
