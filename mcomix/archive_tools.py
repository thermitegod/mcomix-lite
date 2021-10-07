# -*- coding: utf-8 -*-

"""archive_tools.py - Archive tool functions"""

from pathlib import Path

from mcomix.archive.format_libarchive import LibarchiveExtractor

#from mcomix.archive.format_rar import RarArchive
#from mcomix.archive.format_sevenzip import SevenZipArchive
#from mcomix.archive.format_tar import TarArchive
#from mcomix.archive.format_zip import ZipArchive
from mcomix.constants import Constants


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

    def get_archive_handler(self, path: Path, is_archive: bool = False):
        """
        Returns a fitting extractor handler for the archive passed in <path>
        (with optional mime type <type>. Returns None if no matching extractor was found
        """

        if not is_archive:
            return None

        return LibarchiveExtractor(path)

    def get_recursive_archive_handler(self, path: Path, is_archive: bool = False):
        """
        Same as <get_archive_handler> but the handler will transparently handle
        archives within archives
        """

        archive = self.get_archive_handler(path=path, is_archive=is_archive)
        if archive is None:
            return None

        # XXX: Deferred import to avoid circular dependency
        from mcomix.archive.archive_recursive import ArchiveRecursive
        return ArchiveRecursive(archive=archive)


ArchiveTools = _ArchiveTools()
