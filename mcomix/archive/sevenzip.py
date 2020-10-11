# -*- coding: utf-8 -*-

"""7z archive extractor"""

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from loguru import logger

from mcomix.archive.archive_base import BaseArchive
from mcomix.lib import process


class SevenZipArchive(BaseArchive):
    """
    7z file extractor using the 7z executable
    """

    STATE_HEADER, STATE_LISTING, STATE_FOOTER = 1, 2, 3

    def __init__(self, archive: str):
        super().__init__(archive)

        self.__sevenzip = SevenzipExecutable.sevenzip_executable

        self.__contents = []

        self.__state = None
        self.__path = None

    def _get_list_arguments(self):
        return [self.__sevenzip, 'l', '-slt', '--', self.archive]

    def _get_extract_arguments(self, list_file=None):
        if list_file is None:
            return [self.__sevenzip, 'x', '-so', '--', self.archive]
        return [self.__sevenzip, 'x', '-so', '-i@' + list_file, '--', self.archive]

    def _parse_list_output_line(self, line: str):
        """
        Start parsing after the first delimiter (bunch of - characters),
        and end when delimiters appear again. Format:
        Date <space> Time <space> Attr <space> Size <space> Compressed <space> Name
        """

        if line.startswith('----------'):
            if self.__state == self.STATE_HEADER:
                # First delimiter reached, start reading from next line.
                self.__state = self.STATE_LISTING
            elif self.__state == self.STATE_LISTING:
                # Last delimiter read, stop reading from now on.
                self.__state = self.STATE_FOOTER

            return None

        if self.__state == self.STATE_HEADER:
            pass
        elif self.__state == self.STATE_LISTING:
            if line.startswith('Path = '):
                self.__path = line[7:]
                return self.__path
            elif line.startswith('Size = '):
                filesize = int(line[7:])
                if filesize > 0:
                    self.__contents.append((self.__path, filesize))

        return None

    def iter_contents(self):
        #: Indicates which part of the file listing has been read.
        self.__state = self.STATE_HEADER
        #: Current path while listing contents.
        self.__path = None
        with process.popen(self._get_list_arguments(),
                           stderr=process.STDOUT,
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
        with NamedTemporaryFile(mode='wt', prefix='mcomix.7z.') as tmplistfile:
            tmplistfile.write('filename\n')
            tmplistfile.flush()
            with self._create_file(destination_path) as output:
                process.call(self._get_extract_arguments(list_file=tmplistfile.name), stdout=output)
        return destination_path

    def iter_extract(self, entries, destination_dir: Path):
        with process.popen(self._get_extract_arguments()) as proc:
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

    @staticmethod
    def is_available():
        return bool(SevenzipExecutable.sevenzip_executable)


class _SevenzipExecutable:
    def __init__(self):
        super().__init__()

        self.sevenzip_executable = self.find_sevenzip()

    @staticmethod
    def find_sevenzip():
        """
        Tries to start 7z, and returns either '7z' if
        it was started successfully or None otherwise

        :returns: path to 7z
        :rtype: str
        """

        sevenzip = shutil.which('7z')
        if sevenzip is None:
            logger.error(f'failed to find 7z executable')

        return sevenzip


# Singleton instance
SevenzipExecutable = _SevenzipExecutable()

