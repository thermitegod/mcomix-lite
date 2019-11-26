# -*- coding: utf-8 -*-

"""archive_tools.py - Archive tool functions"""

import os
import zipfile

from mcomix import constants, log
from mcomix.archive import pdf, rar, sevenzip, zip

# Handlers for each archive type.
_HANDLERS = {
    constants.ZIP: (zip.ZipArchive,),
    constants.ZIP_EXTERNAL: (sevenzip.SevenZipArchive,),
    constants.RAR: (rar.RarArchive,),
    constants.LHA: (sevenzip.SevenZipArchive,),
    constants.SEVENZIP: (sevenzip.SevenZipArchive,),
    constants.PDF: (pdf.PdfArchive,),
}


def _getext(path):
    """Get extension of archive"""
    b, e = os.path.splitext(path.lower())
    return e


def _get_handler(archive_type):
    """Return best archive class for format <archive_type>"""
    for handler in _HANDLERS[archive_type]:
        if not hasattr(handler, 'is_available'):
            return handler
        if handler.is_available():
            return handler


def _is_available(archive_type):
    """Return True if a handler supporting the <archive_type> format is available"""
    return _get_handler(archive_type) is not None


def szip_available():
    return _is_available(constants.SEVENZIP)


def rar_available():
    return _is_available(constants.RAR)


def lha_available():
    return _is_available(constants.LHA)


def pdf_available():
    return _is_available(constants.PDF)


SUPPORTED_ARCHIVE_EXTS = set()
SUPPORTED_ARCHIVE_FORMATS = {}


def init_supported_formats():
    for name, formats, is_available in (
            ('ZIP', constants.ZIP_FORMATS, True),
            ('RAR', constants.RAR_FORMATS, rar_available()),
            ('7z', constants.SZIP_FORMATS, szip_available()),
            ('LHA', constants.LHA_FORMATS, lha_available()),
            ('PDF', constants.PDF_FORMATS, pdf_available()),
    ):
        if not is_available:
            continue
        SUPPORTED_ARCHIVE_FORMATS[name] = (set(), set())
        for ext, mime in formats:
            SUPPORTED_ARCHIVE_FORMATS[name][0].add(mime.lower())
            SUPPORTED_ARCHIVE_FORMATS[name][1].add(ext.lower())
        # also add to supported extensions list
        SUPPORTED_ARCHIVE_EXTS.update(SUPPORTED_ARCHIVE_FORMATS[name][1])


def get_supported_formats():
    if not SUPPORTED_ARCHIVE_FORMATS:
        init_supported_formats()
    return SUPPORTED_ARCHIVE_FORMATS


def is_archive_file(path):
    if not SUPPORTED_ARCHIVE_FORMATS:
        init_supported_formats()
    return path.lower().endswith(tuple(SUPPORTED_ARCHIVE_EXTS))


def archive_mime_type(path):
    """Return the archive type of <path> or None for non-archives"""
    try:
        if os.path.isfile(path):
            if not os.access(path, os.R_OK):
                return None

            if zipfile.is_zipfile(path):
                if zip.is_py_supported_zipfile(path):
                    return constants.ZIP
                else:
                    return constants.ZIP_EXTERNAL

            with open(path, 'rb') as fd:
                magic = fd.read(10)

            if magic.startswith(b'Rar!\x1a\x07'):
                return constants.RAR

            if magic[0:6] == b'7z\xbc\xaf\x27\x1c':
                return constants.SEVENZIP

            if magic[2:].startswith((b'-lh', b'-lz')):
                return constants.LHA

            if magic[0:4] == b'%PDF':
                return constants.PDF

    except Exception:
        log.warning(f'Could not read {path}')

    return None


def get_archive_handler(path, type=None):
    """Returns a fitting extractor handler for the archive passed in <path>
    (with optional mime type <type>. Returns None if no matching extractor was found"""
    if type is None:
        type = archive_mime_type(path)
        if type is None:
            return None

    handler = _get_handler(type)
    if handler is None:
        return None

    return handler(path)


def get_recursive_archive_handler(path, type=None, **kwargs):
    """Same as <get_archive_handler> but the handler will transparently handle
    archives within archives"""
    archive = get_archive_handler(path, type=type)
    if archive is None:
        return None
    # XXX: Deferred import to avoid circular dependency
    from mcomix.archive import archive_recursive
    return archive_recursive.RecursiveArchive(archive, **kwargs)
