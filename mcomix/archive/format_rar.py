# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.archive.archive_executable import BaseArchiveExecutable
from mcomix.lib.executable import GetExecutable


class RarArchive(BaseArchiveExecutable):
    """
    RAR file extractor using the unrar executable
    """

    def __init__(self, archive: Path):
        super().__init__(archive)

        self.__executable = GetExecutable.executables['UNRAR']['PATH']

    @staticmethod
    def is_available():
        return GetExecutable.executables['UNRAR']['FOUND']

    def _get_list_arguments(self):
        return [self.__executable, 'vt', '--', self.archive]

    def _get_extract_arguments(self):
        return [self.__executable, 'p', '-inul', '-@', '--', self.archive]

    def _parse_list_output_line(self, line: str):
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
