# -*- coding: utf-8 -*-

"""archive_tools.py - Archive tool functions"""

from pathlib import Path

from mcomix.archive.format_rar import RarArchive
from mcomix.archive.format_sevenzip import SevenZipArchive
from mcomix.archive.format_tar import TarArchive
from mcomix.archive.format_zip import ZipArchive
from mcomix.constants import Constants


class _ArchiveTools:
    def __init__(self):
        super().__init__()

        # Handlers for each archive type.
        self.__handlers = {
            Constants.ARCHIVE_FORMATS['ZIP']: ZipArchive,
            Constants.ARCHIVE_FORMATS['SEVENZIP']: SevenZipArchive,
            Constants.ARCHIVE_FORMATS['RAR']: RarArchive,
            Constants.ARCHIVE_FORMATS['TAR']: TarArchive,
        }

        self.__ext_zip = [mime.ext for mime in Constants.MIME_FORMAT['ZIP']]
        self.__ext_szip = [mime.ext for mime in Constants.MIME_FORMAT['SEVENZIP']]
        self.__ext_rar = [mime.ext for mime in Constants.MIME_FORMAT['RAR']]
        self.__ext_tar = [mime.ext for mime in Constants.MIME_FORMAT['TAR']]

        self.__supported_archive_ext = [*self.__ext_zip, *self.__ext_szip,
                                        *self.__ext_rar, *self.__ext_tar]

    @property
    def supported_archive_ext(self):
        return self.__supported_archive_ext

    def is_archive_file(self, path: Path):
        return path.suffix.lower() in self.__supported_archive_ext

    def archive_mime_type(self, path: Path):
        """
        Return the archive type of <path> or None for non-archives
        """

        if not self.is_archive_file(path=path):
            return None

        ext = path.suffix.lower()
        if ext in self.__ext_zip:
            return Constants.ARCHIVE_FORMATS['ZIP']
        elif ext in self.__ext_szip:
            return Constants.ARCHIVE_FORMATS['SEVENZIP']
        elif ext in self.__ext_rar:
            return Constants.ARCHIVE_FORMATS['RAR']
        elif ext in self.__ext_tar:
            return Constants.ARCHIVE_FORMATS['TAR']
        else:
            raise ValueError

    def get_archive_handler(self, path: Path, archive_type: int = None):
        """
        Returns a fitting extractor handler for the archive passed in <path>
        (with optional mime type <type>. Returns None if no matching extractor was found
        """

        if archive_type is None:
            return None

        return self.__handlers[archive_type](path)

    def get_recursive_archive_handler(self, path: Path, archive_type: int = None):
        """
        Same as <get_archive_handler> but the handler will transparently handle
        archives within archives
        """

        archive = self.get_archive_handler(path=path, archive_type=archive_type)
        if archive is None:
            return None

        # XXX: Deferred import to avoid circular dependency
        from mcomix.archive.archive_recursive import ArchiveRecursive
        return ArchiveRecursive(archive=archive)


ArchiveTools = _ArchiveTools()
