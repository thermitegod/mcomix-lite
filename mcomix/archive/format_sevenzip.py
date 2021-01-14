# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.archive.archive_external import ArchiveExternal
from mcomix.lib.executable import GetExecutable


class SevenZipArchive(ArchiveExternal):
    """
    7z file extractor using the 7z executable
    """

    def __init__(self, archive: Path):
        super().__init__(archive)

        self.__executable = GetExecutable.executables['SZIP']['PATH']

    @staticmethod
    def is_available():
        return GetExecutable.executables['SZIP']['FOUND']

    def _get_list_arguments(self):
        return [self.__executable, 'l', '-slt', '--', self.archive]

    def _get_extract_arguments(self):
        return [self.__executable, 'x', '-so', '--', self.archive]

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
