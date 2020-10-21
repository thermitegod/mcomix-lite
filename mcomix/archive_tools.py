# -*- coding: utf-8 -*-

"""archive_tools.py - Archive tool functions"""

from pathlib import Path

from mcomix.archive.format_rar import RarArchive
from mcomix.archive.format_sevenzip import SevenZipArchive
from mcomix.archive.format_zip import ZipArchive
from mcomix.constants import Constants


class _ArchiveTools:
    def __init__(self):
        super().__init__()

        self.__supported_archive_ext = ()

        self.__zip_ext = ()
        self.__sevenzip_ext = ()
        self.__rar_ext = ()

        # Handlers for each archive type.
        self.__handlers = {
            Constants.ZIP: (ZipArchive,),
            Constants.SEVENZIP: (SevenZipArchive,),
            Constants.RAR: (RarArchive,),
        }

        self.init_supported_formats()

    @staticmethod
    def _create_ext_tuple(archive_format):
        return tuple([ext[0] for ext in archive_format])

    def init_supported_formats(self):
        if ZipArchive.is_available():
            self.__zip_ext = self._create_ext_tuple(Constants.ZIP_FORMATS)
        if SevenZipArchive.is_available():
            self.__sevenzip_ext = self._create_ext_tuple(Constants.SZIP_FORMATS)
        if RarArchive.is_available():
            self.__rar_ext = self._create_ext_tuple(Constants.RAR_FORMATS)

        self.__supported_archive_ext = self.__zip_ext + self.__sevenzip_ext + self.__rar_ext

    def is_archive_file(self, path: Path):
        return str(path).lower().endswith(self.__supported_archive_ext)

    def archive_mime_type(self, path: Path):
        """
        Return the archive type of <path> or None for non-archives
        """

        if self.is_archive_file(path=path):
            filename = str(path).lower()
            if filename.endswith(self.__zip_ext):
                return Constants.ZIP
            elif filename.endswith(self.__sevenzip_ext):
                return Constants.SEVENZIP
            elif filename.endswith(self.__rar_ext):
                return Constants.RAR

        return None

    def get_archive_handler(self, path: Path, archive_type=None):
        """
        Returns a fitting extractor handler for the archive passed in <path>
        (with optional mime type <type>. Returns None if no matching extractor was found
        """

        if archive_type is None:
            archive_type = self.archive_mime_type(path=path)
            if archive_type is None:
                return None

        for handler in self.__handlers[archive_type]:
            if handler.is_available():
                return handler(path)

        return None

    def get_recursive_archive_handler(self, path: Path, archive_type=None, **kwargs):
        """
        Same as <get_archive_handler> but the handler will transparently handle
        archives within archives
        """

        archive = self.get_archive_handler(path=path, archive_type=archive_type)
        if archive is None:
            return None

        # XXX: Deferred import to avoid circular dependency
        from mcomix.archive.archive_recursive import RecursiveArchive
        return RecursiveArchive(archive, **kwargs)


ArchiveTools = _ArchiveTools()
