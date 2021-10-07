# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.archive.archive_external import ArchiveExternal


class TarArchive(ArchiveExternal):
    """
    TAR file extractor using the tar executable
    """

    def __init__(self, archive: Path):
        super().__init__(archive)

    def _get_list_arguments(self):
        return ['tar', '--list', '-vf', self.archive]

    def _get_extract_arguments(self):
        return ['tar', '--extract', '--to-stdout', '-f', self.archive]

    def _parse_list_output_line(self, line: str):
        line = line.split()

        filesize = int(line[2])
        self.path = line[5]

        if filesize > 0:
            self.contents.append((self.path, filesize))

        return self.path
