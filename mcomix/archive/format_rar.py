# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.archive.archive_external import ArchiveExternal


class RarArchive(ArchiveExternal):
    """
    RAR file extractor using the unrar executable
    """

    def __init__(self, archive: Path):
        super().__init__(archive)

    def _get_list_arguments(self):
        return ['unrar', 'vt', '--', self.archive]

    def _get_extract_arguments(self):
        return ['unrar', 'p', '-inul', '-@', '--', self.archive]

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
