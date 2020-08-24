# -*- coding: utf-8 -*-

"""archive_tools.py - Archive tool functions"""

import os
import zipfile
from pathlib import Path

from loguru import logger

from mcomix import constants
from mcomix.archive import rar, sevenzip, zip

# Handlers for each archive type.
_HANDLERS = {
    constants.ZIP: (zip.ZipArchive,),
    constants.SEVENZIP: (sevenzip.SevenZipArchive,),
    constants.RAR: (rar.RarArchive,),
}


def _get_handler(archive_type):
    """
    :returns: Return best archive class for format <archive_type>
    """

    for handler in _HANDLERS[archive_type]:
        if not hasattr(handler, 'is_available'):
            return handler
        if handler.is_available():
            return handler


def _is_available(archive_type):
    """
    :returns: Return True if a handler supporting the <archive_type> format is available
    """

    return _get_handler(archive_type) is not None


def szip_available():
    return _is_available(constants.SEVENZIP)


def rar_available():
    return _is_available(constants.RAR)


SUPPORTED_ARCHIVE_EXTS = set()
SUPPORTED_ARCHIVE_FORMATS = {}


def init_supported_formats():
    for name, formats, is_available in (
            ('ZIP', constants.ZIP_FORMATS, True),
            ('7z', constants.SZIP_FORMATS, szip_available()),
            ('RAR', constants.RAR_FORMATS, rar_available()),
    ):
        if not is_available:
            continue
        SUPPORTED_ARCHIVE_FORMATS[name] = (set(), set())
        for ext, mime in formats:
            SUPPORTED_ARCHIVE_FORMATS[name][0].add(mime.lower())
            SUPPORTED_ARCHIVE_FORMATS[name][1].add(ext.lower())
        # also add to supported extensions list
        SUPPORTED_ARCHIVE_EXTS.update(SUPPORTED_ARCHIVE_FORMATS[name][1])


def is_archive_file(path):
    if not SUPPORTED_ARCHIVE_FORMATS:
        init_supported_formats()
    return str(path).lower().endswith(tuple(SUPPORTED_ARCHIVE_EXTS))


def archive_mime_type(path):
    """
    Return the archive type of <path> or None for non-archives
    """

    try:
        path = Path() / path
        if Path.is_file(path):
            if not os.access(path, os.R_OK):
                return None

            if zipfile.is_zipfile(path):
                return constants.ZIP

            with Path.open(path, 'rb') as fd:
                magic = fd.read(10)

            if magic[0:6] == b'7z\xbc\xaf\x27\x1c':
                return constants.SEVENZIP
            elif magic.startswith(b'Rar!\x1a\x07'):
                return constants.RAR

            return None

    except Exception:
        logger.warning(f'Could not read: \'{path}\'')
        return None


def get_archive_handler(path, archive_type=None):
    """
    Returns a fitting extractor handler for the archive passed in <path>
    (with optional mime type <type>. Returns None if no matching extractor was found
    """

    if archive_type is None:
        archive_type = archive_mime_type(path)
        if archive_type is None:
            return None

    handler = _get_handler(archive_type)
    if handler is None:
        return None

    return handler(path)


def get_recursive_archive_handler(path, archive_type=None, **kwargs):
    """
    Same as <get_archive_handler> but the handler will transparently handle
    archives within archives
    """

    archive = get_archive_handler(path, archive_type=archive_type)
    if archive is None:
        return None

    # XXX: Deferred import to avoid circular dependency
    from mcomix.archive import archive_recursive
    return archive_recursive.RecursiveArchive(archive, **kwargs)
