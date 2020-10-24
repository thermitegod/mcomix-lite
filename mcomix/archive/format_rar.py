# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

from loguru import logger

from mcomix.archive.archive_executable import BaseArchiveExecutable
from mcomix.lib.process import Process


class RarArchive(BaseArchiveExecutable):
    """
    RAR file extractor using the unrar executable
    """

    def __init__(self, archive):
        super().__init__(archive)

        self.__unrar = RarExecutable.unrar_executable

    @staticmethod
    def is_available():
        return bool(RarExecutable.unrar_executable)

    def _get_list_arguments(self):
        return [self.__unrar, 'vt', '--', self.archive]

    def _get_extract_arguments(self):
        return [self.__unrar, 'p', '-inul', '-@', '--', self.archive]

    def _parse_list_output_line(self, line):
        if self.state == self.STATE_HEADER:
            if line.startswith('Details: '):
                self.state = self.STATE_LISTING
                return None
        if self.state == self.STATE_LISTING:
            line = line.lstrip()
            if line.startswith('Name: '):
                self.path = line[6:]
                return self.path
            if line.startswith('Size: '):
                filesize = int(line[6:])
                if filesize > 0:
                    self.contents.append((self.path, filesize))
        return None

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

        destination_path = Path() / destination_dir / filename

        with self._create_file(destination_path) as output:
            Process.call(self._get_extract_arguments(), stdout=output)
        return destination_path


class _RarExecutable:
    def __init__(self):
        super().__init__()

        self.unrar_executable = self.find_unrar()

    @staticmethod
    def find_unrar():
        """
        Tries to load libunrar and will return a handle of it.
        Returns None if an error occured or the library couldn't be found

        :returns: loaded unrar library
        """

        unrar = shutil.which('unrar')
        if unrar is None:
            logger.error(f'failed to find unrar executable')

        return unrar


# Singleton instance
RarExecutable = _RarExecutable()
