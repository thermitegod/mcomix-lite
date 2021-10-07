# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.archive.archive_external import ArchiveExternal


class ZipArchive(ArchiveExternal):
    """
    ZIP file extractor using the zip executable
    """

    def __init__(self, archive: Path):
        super().__init__(archive)

    def _get_list_arguments(self):
        return ['unzip', '-v', '--', self.archive]

    def _get_extract_arguments(self):
        return ['unzip', '-p', '--', self.archive]

    def _parse_list_output_line(self, line: str):
        line = line.split()

        try:
            filesize = int(line[0])
            self.path = line[7]
        except (ValueError, IndexError):
            # ValueError, comes from getting filesize
            # IndexError, comes from getting self.path
            return None

        if filesize > 0:
            self.contents.append((self.path, filesize))

        return self.path
