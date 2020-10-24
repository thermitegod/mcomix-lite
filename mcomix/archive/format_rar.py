# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.archive.archive_executable import BaseArchiveExecutable
from mcomix.lib.process import Process, GetExecutable


class RarArchive(BaseArchiveExecutable):
    """
    RAR file extractor using the unrar executable
    """

    def __init__(self, archive):
        super().__init__(archive)

        self.__executable = Executable.executable

    @staticmethod
    def is_available():
        return bool(Executable.executable)

    def _get_list_arguments(self):
        return [self.__executable, 'vt', '--', self.archive]

    def _get_extract_arguments(self):
        return [self.__executable, 'p', '-inul', '-@', '--', self.archive]

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


class _Executable:
    def __init__(self):
        super().__init__()

        self.executable = GetExecutable('unrar').executable


Executable = _Executable()
