# -*- coding: utf-8 -*-

import tarfile
from pathlib import Path

from loguru import logger

from mcomix.archive.archive_builtin import ArchiveBuiltin


class TarArchive(ArchiveBuiltin):
    def __init__(self, archive: Path):
        super().__init__(archive)

        self.__tar = tarfile.open(archive, mode='r')

        # tarfile is not thread-safe
        # so use OrderedDict to save TarInfo in order
        # {unicode_name: TarInfo}
        for member in self.__tar.getmembers():
            self.contents_info[member.name] = member

    def extract(self, filename: str, destination_dir: Path):
        """
        Extract <filename> from the archive to <destination_dir>

        :param filename: file to extract
        :param destination_dir: extraction path
        :returns: full path of the extracted file
        """

        with self.lock:
            info = self.contents_info[filename]
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
