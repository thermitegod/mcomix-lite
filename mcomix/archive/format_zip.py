# -*- coding: utf-8 -*-

import zipfile
from pathlib import Path

from loguru import logger

from mcomix.archive.archive_builtin import ArchiveBuiltin


class ZipArchive(ArchiveBuiltin):
    def __init__(self, archive: Path):
        super().__init__(archive)

        self.__zip = zipfile.ZipFile(archive, 'r')

        # zipfile is usually not thread-safe
        # so use OrderedDict to save ZipInfo in order
        # {unicode_name: ZipInfo}
        for info in self.__zip.infolist():
            self.contents_info[info.filename] = info

    def extract(self, filename: str, destination_dir: Path):
        """
        Extract <filename> from the archive to <destination_dir>

        :param filename: file to extract
        :param destination_dir: extraction path
        """

        with self.lock:
            info = self.contents_info[filename]
            data = self.__zip.read(info)

        destination_path = Path() / destination_dir / filename
        with self._create_file(destination_path) as new:
            filelen = new.write(data)

        if filelen != info.file_size:
            logger.warning(f'{filename}: extracted size is {filelen} bytes, but should be {info.file_size} bytes')

    def close(self):
        self.__zip.close()
