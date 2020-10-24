# -*- coding: utf-8 -*-

"""7z archive extractor"""

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from loguru import logger

from mcomix.archive.archive_executable import BaseArchiveExecutable
from mcomix.lib.process import Process


class SevenZipArchive(BaseArchiveExecutable):
    """
    7z file extractor using the 7z executable
    """

    def __init__(self, archive: Path):
        super().__init__(archive)

        self.__sevenzip = SevenzipExecutable.sevenzip_executable

    @staticmethod
    def is_available():
        return bool(SevenzipExecutable.sevenzip_executable)

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
            if self.state == self.STATE_HEADER:
                # First delimiter reached, start reading from next line.
                self.state = self.STATE_LISTING
            elif self.state == self.STATE_LISTING:
                # Last delimiter read, stop reading from now on.
                self.state = self.STATE_FOOTER

            return None

        if self.state == self.STATE_HEADER:
            pass
        elif self.state == self.STATE_LISTING:
            if line.startswith('Path = '):
                self.path = line[7:]
                return self.path
            elif line.startswith('Size = '):
                filesize = int(line[7:])
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
        with NamedTemporaryFile(mode='wt', prefix='mcomix.7z.') as tmplistfile:
            tmplistfile.write('filename\n')
            tmplistfile.flush()
            with self._create_file(destination_path) as output:
                Process.call(self._get_extract_arguments(list_file=tmplistfile.name), stdout=output)
        return destination_path


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
