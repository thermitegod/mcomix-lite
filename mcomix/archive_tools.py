# -*- coding: utf-8 -*-

"""archive_tools.py - Archive tool functions"""

from pathlib import Path


class _ArchiveTools:
    def __init__(self):
        super().__init__()

        self.__supported_archive_ext = (
            '.zip', '.cbz',
            '.rar', '.bcr',
            '.7z', '.cb7',
            '.tar', '.cbt',
            '.gz', '.bz2', '.lzma', '.xz', '.zst',
        )

    @property
    def supported_archive_ext(self):
        return self.__supported_archive_ext

    def is_archive_file(self, path: Path):
        return path.suffix.lower() in self.__supported_archive_ext


ArchiveTools = _ArchiveTools()
