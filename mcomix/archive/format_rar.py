# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

from loguru import logger

from mcomix.archive.archive_base import BaseArchive
from mcomix.lib.process import Process


class RarArchive(BaseArchive):
    """
    RAR file extractor using the unrar executable
    """

    STATE_HEADER, STATE_LISTING = 1, 2

    def __init__(self, archive):
        super().__init__(archive)

        self.__unrar = RarExecutable.unrar_executable

        self.__state = None
        self.__path = None

        self.__contents = []

    @staticmethod
    def is_available():
        return bool(RarExecutable.unrar_executable)

    def _get_list_arguments(self):
        return [self.__unrar, 'vt', '--', self.archive]

    def _get_extract_arguments(self):
        return [self.__unrar, 'p', '-inul', '-@', '--', self.archive]

    def _parse_list_output_line(self, line):
        if self.__state == self.STATE_HEADER:
            if line.startswith('Details: '):
                self.__state = self.STATE_LISTING
                return None
        if self.__state == self.STATE_LISTING:
            line = line.lstrip()
            if line.startswith('Name: '):
                self.__path = line[6:]
                return self.__path
            if line.startswith('Size: '):
                filesize = int(line[6:])
                if filesize > 0:
                    self.__contents.append((self.__path, filesize))
        return None

    def iter_contents(self):
        #: Indicates which part of the file listing has been read.
        self.__state = self.STATE_HEADER
        #: Current path while listing contents.
        self.__path = None
        with Process.popen(self._get_list_arguments(),
                           stderr=Process.STDOUT,
                           universal_newlines=True) as proc:
            for line in proc.stdout:
                filename = self._parse_list_output_line(line.rstrip('\n'))
                if filename is not None:
                    yield filename

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

    def iter_extract(self, entries, destination_dir: Path):
        with Process.popen(self._get_extract_arguments()) as proc:
            wanted = dict([(unicode_name, unicode_name) for unicode_name in entries])

            for filename, filesize in self.__contents:
                data = proc.stdout.read(filesize)
                if filename not in wanted:
                    continue
                unicode_name = wanted.get(filename, None)
                if unicode_name is None:
                    continue

                destination_path = Path() / destination_dir / unicode_name
                with self._create_file(destination_path) as new:
                    new.write(data)
                yield unicode_name
                del wanted[filename]
                if not wanted:
                    break


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
