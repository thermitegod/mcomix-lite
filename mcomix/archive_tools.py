# -*- coding: utf-8 -*-

"""archive_tools.py - Archive tool functions"""

from pathlib import Path

from mcomix.archive.archive_interface import ArchiveInterface
from mcomix.archive.format_rar import RarArchive
from mcomix.archive.format_sevenzip import SevenZipArchive
from mcomix.archive.format_tar import TarArchive
from mcomix.archive.format_zip import ZipArchive
from mcomix.constants import Constants


class _ArchiveTools:
    def __init__(self):
        super().__init__()

        self.__supported_archive_ext = []

        self.__ext_zip = []
        self.__ext_sevenzip = []
        self.__ext_rar = []
        self.__ext_tar = []

        # Handlers for each archive type.
        self.__handlers = {
            Constants.ARCHIVE_FORMATS['ZIP']: ZipArchive,
            Constants.ARCHIVE_FORMATS['SEVENZIP']: SevenZipArchive,
            Constants.ARCHIVE_FORMATS['RAR']: RarArchive,
            Constants.ARCHIVE_FORMATS['TAR']: TarArchive,
        }

        self.init_supported_formats()

    @staticmethod
    def _create_ext_list(archive_format: tuple):
        return [ext[0] for ext in archive_format]

    def init_supported_formats(self):
        if ZipArchive.is_available():
            self.__ext_zip = self._create_ext_list(Constants.MIME_FORMAT['ZIP'])
            self.__supported_archive_ext += self.__ext_zip
        if SevenZipArchive.is_available():
            self.__ext_sevenzip = self._create_ext_list(Constants.MIME_FORMAT['SEVENZIP'])
            self.__supported_archive_ext += self.__ext_sevenzip
        if RarArchive.is_available():
            self.__ext_rar = self._create_ext_list(Constants.MIME_FORMAT['RAR'])
            self.__supported_archive_ext += self.__ext_rar
        if TarArchive.is_available():
            self.__ext_tar = self._create_ext_list(Constants.MIME_FORMAT['TAR'])
            self.__supported_archive_ext += self.__ext_tar

    def is_archive_file(self, path: Path):
        return path.suffix.lower() in self.__supported_archive_ext

    def archive_mime_type(self, path: Path):
        """
        Return the archive type of <path> or None for non-archives
        """

        if not self.is_archive_file(path=path):
            return None

        if path.suffix in self.__ext_zip:
            return Constants.ARCHIVE_FORMATS['ZIP']
        elif path.suffix in self.__ext_sevenzip:
            return Constants.ARCHIVE_FORMATS['SEVENZIP']
        elif path.suffix in self.__ext_rar:
            return Constants.ARCHIVE_FORMATS['RAR']
        elif path.suffix in self.__ext_tar:
            return Constants.ARCHIVE_FORMATS['TAR']

    def get_archive_handler(self, path: Path, archive_type=None):
        """
        Returns a fitting extractor handler for the archive passed in <path>
        (with optional mime type <type>. Returns None if no matching extractor was found
        """

        if archive_type is None:
            archive_type = self.archive_mime_type(path=path)
            if archive_type is None:
                return None

        if self.__handlers[archive_type].is_available():
            return self.__handlers[archive_type](path)

        return None

    def get_archive_interface_handler(self, path: Path, archive_type=None):
        archive = self.get_archive_handler(path=path, archive_type=archive_type)
        if archive is None:
            return None

        return ArchiveInterface(archive)


ArchiveTools = _ArchiveTools()
