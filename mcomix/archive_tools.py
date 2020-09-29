# -*- coding: utf-8 -*-

"""archive_tools.py - Archive tool functions"""

import os
import zipfile
from pathlib import Path

from loguru import logger

from mcomix import constants
from mcomix.archive.rar import RarArchive
from mcomix.archive.sevenzip import SevenZipArchive
from mcomix.archive.zip import ZipArchive


class _ArchiveTools:
    def __init__(self):
        super().__init__()

        self.__supported_archive_ext = set()
        self.__supported_archive_formats = {}

        # Handlers for each archive type.
        self.__handlers = {
            constants.ZIP: (ZipArchive,),
            constants.SEVENZIP: (SevenZipArchive,),
            constants.RAR: (RarArchive,),
        }

        self.init_supported_formats()

    def init_supported_formats(self):
        for name, formats, is_available in (
                ('ZIP', constants.ZIP_FORMATS, self._get_handler(constants.ZIP)),
                ('7z', constants.SZIP_FORMATS, self._get_handler(constants.SEVENZIP)),
                ('RAR', constants.RAR_FORMATS, self._get_handler(constants.RAR)),
        ):
            if not is_available:
                continue
            self.__supported_archive_formats[name] = (set(), set())
            for ext, mime in formats:
                self.__supported_archive_formats[name][0].add(mime.lower())
                self.__supported_archive_formats[name][1].add(ext.lower())
            # also add to supported extensions list
            self.__supported_archive_ext.update(self.__supported_archive_formats[name][1])

    def _get_handler(self, archive_type):
        """
        :returns: Return best archive class for format <archive_type>
        """

        for handler in self.__handlers[archive_type]:
            if handler.is_available():
                return handler
            else:
                return False

    def is_archive_file(self, path: Path):
        return str(path).lower().endswith(tuple(self.__supported_archive_ext))

    @staticmethod
    def archive_mime_type(path: Path):
        """
        Return the archive type of <path> or None for non-archives
        """

        try:
            if Path.is_file(path):
                if not os.access(path, os.R_OK):
                    return None

                if zipfile.is_zipfile(path):
                    return constants.ZIP

                with Path.open(path, mode='rb') as fd:
                    magic = fd.read(10)

                if magic[0:6] == b'7z\xbc\xaf\x27\x1c':
                    return constants.SEVENZIP
                elif magic.startswith(b'Rar!\x1a\x07'):
                    return constants.RAR

                return None

        except Exception:
            logger.warning(f'Could not read: \'{path}\'')
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

        handler = self._get_handler(archive_type=archive_type)
        if handler is None:
            return None

        return handler(str(path))

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
