# -*- coding: utf-8 -*-

"""Glue around libunrar.so to extract RAR files without having to
resort to calling rar/unrar manually"""

import ctypes
import ctypes.util
import os

from loguru import logger

from mcomix.archive import archive_base

# Filled on-demand by _get_unrar
_unrar_dll = None

UNRARCALLBACK = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_uint, ctypes.c_long, ctypes.c_long, ctypes.c_long)


class RarArchive(archive_base.BaseArchive):
    """Wrapper class for libunrar. All string values passed to this class must be unicode objects.
    In turn, all values returned are also unicode"""
    # Nope! Not a good idea...
    support_concurrent_extractions = False

    class _OpenMode:
        """Rar open mode"""
        RAR_OM_EXTRACT = 1

    class _ProcessingMode:
        """Rar file processing mode"""
        RAR_SKIP = 0
        RAR_EXTRACT = 2

    class _ErrorCode:
        """Rar error codes"""
        ERAR_END_ARCHIVE = 10
        ERAR_NO_MEMORY = 11
        ERAR_BAD_DATA = 12
        ERAR_BAD_ARCHIVE = 13
        ERAR_UNKNOWN_FORMAT = 14
        ERAR_EOPEN = 15
        ERAR_ECREATE = 16
        ERAR_ECLOSE = 17
        ERAR_EREAD = 18
        ERAR_EWRITE = 19
        ERAR_SMALL_BUF = 20
        ERAR_UNKNOWN = 21
        ERAR_MISSING_PASSWORD = 22

    class _RAROpenArchiveDataEx(ctypes.Structure):
        """Archive header structure. Used by DLL calls"""
        _pack_ = 1
        _fields_ = [
            ('ArcName', ctypes.c_char_p),
            ('ArcNameW', ctypes.c_wchar_p),
            ('OpenMode', ctypes.c_uint),
            ('OpenResult', ctypes.c_uint),
            ('CmtBuf', ctypes.c_char_p),
            ('CmtBufSize', ctypes.c_uint),
            ('CmtSize', ctypes.c_uint),
            ('CmtState', ctypes.c_uint),
            ('Flags', ctypes.c_uint),
            ('Callback', UNRARCALLBACK),
            ('UserData', ctypes.c_long),
            ('Reserved', ctypes.c_uint * 28),
        ]

    class _RARHeaderDataEx(ctypes.Structure):
        """Archive file structure. Used by DLL calls"""
        _pack_ = 1
        _fields_ = [
            ('ArcName', ctypes.c_char * 1024),
            ('ArcNameW', ctypes.c_wchar * 1024),
            ('FileName', ctypes.c_char * 1024),
            ('FileNameW', ctypes.c_wchar * 1024),
            ('Flags', ctypes.c_uint),
            ('PackSize', ctypes.c_uint),
            ('PackSizeHigh', ctypes.c_uint),
            ('UnpSize', ctypes.c_uint),
            ('UnpSizeHigh', ctypes.c_uint),
            ('HostOS', ctypes.c_uint),
            ('FileCRC', ctypes.c_uint),
            ('FileTime', ctypes.c_uint),
            ('UnpVer', ctypes.c_uint),
            ('Method', ctypes.c_uint),
            ('FileAttr', ctypes.c_uint),
            ('CmtBuf', ctypes.c_char_p),
            ('CmtBufSize', ctypes.c_uint),
            ('CmtSize', ctypes.c_uint),
            ('CmtState', ctypes.c_uint),
            ('Reserved', ctypes.c_uint * 1024),
        ]

    @staticmethod
    def is_available():
        """Returns True if unrar.dll can be found, False otherwise"""
        return bool(_get_unrar())

    def __init__(self, archive):
        """Initialize Unrar.dll"""
        super(RarArchive, self).__init__(archive)
        self._unrar = _get_unrar()
        self._handle = None
        self._is_solid = False
        # Information about the current file will be stored in this structure
        self._headerdata = RarArchive._RARHeaderDataEx()
        self._current_filename = None

        # Set up function prototypes.
        # Mandatory since pointers get truncated on x64 otherwise!
        self._unrar.RAROpenArchiveEx.restype = ctypes.c_void_p
        self._unrar.RAROpenArchiveEx.argtypes = [ctypes.POINTER(RarArchive._RAROpenArchiveDataEx)]
        self._unrar.RARCloseArchive.restype = ctypes.c_int
        self._unrar.RARCloseArchive.argtypes = [ctypes.c_void_p]
        self._unrar.RARReadHeaderEx.restype = ctypes.c_int
        self._unrar.RARReadHeaderEx.argtypes = [ctypes.c_void_p, ctypes.POINTER(RarArchive._RARHeaderDataEx)]
        self._unrar.RARProcessFileW.restype = ctypes.c_int
        self._unrar.RARProcessFileW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p, ctypes.c_wchar_p]
        self._unrar.RARSetCallback.argtypes = [ctypes.c_void_p, UNRARCALLBACK, ctypes.c_long]

    def is_solid(self):
        return self._is_solid

    def iter_contents(self):
        """List archive contents"""
        self._close()
        self._open()
        try:
            while True:
                self._read_header()
                if 0 != (0x10 & self._headerdata.Flags):
                    self._is_solid = True
                yield (filename := self._current_filename)
                # Skip to the next entry if we're still on the same name
                # (extract may have been called by iter_extract).
                if filename == self._current_filename:
                    self._process()
        except UnrarException as exc:
            logger.error(f'Error while listing contents: {str(exc)}')
        except EOFError:
            # End of archive reached.
            pass
        finally:
            self._close()

    def extract(self, filename, destination_dir):
        """Extract <filename> from the archive to <destination_dir>"""
        if not self._handle:
            self._open()
        looped = False
        destination_path = os.path.join(destination_dir, filename)
        while True:
            # Check if the current entry matches the requested file.
            if self._current_filename is not None:
                if self._current_filename == filename:
                    # It's the entry we're looking for, extract it.
                    dest = ctypes.c_wchar_p(destination_path)
                    self._process(dest)
                    break
                # Not the right entry, skip it.
                self._process()
            try:
                self._read_header()
            except EOFError:
                # Archive end was reached, this might be due to out-of-order
                # extraction while the handle was still open.  Close the
                # archive and jump back to archive start and try to extract
                # file again.  Do this only once; if the file isn't found after
                # a second full pass, it probably doesn't even exist in the
                # archive.
                if looped:
                    break
                self._open()
        # After the method returns, the RAR handler is still open and pointing
        # to the next archive file. This will improve extraction speed for sequential file reads.
        # After all files have been extracted, close() should be called to free the handler resources.
        return destination_path

    def close(self):
        """Close the archive handle"""
        self._close()

    def _open(self):
        """Open rar handle for extraction"""
        archivedata = RarArchive._RAROpenArchiveDataEx(ArcNameW=self.archive,
                                                       OpenMode=RarArchive._OpenMode.RAR_OM_EXTRACT,
                                                       UserData=0)

        if not (handle := self._unrar.RAROpenArchiveEx(ctypes.byref(archivedata))):
            errormessage = UnrarException.get_error_message(archivedata.OpenResult)
            raise UnrarException(f'Could not open archive: {errormessage}')
        self._handle = handle

    def _check_errorcode(self, errorcode):
        if 0 == errorcode:
            # No error.
            return
        self._close()
        if RarArchive._ErrorCode.ERAR_END_ARCHIVE == errorcode:
            # End of archive reached.
            exc = EOFError()
        else:
            errormessage = UnrarException.get_error_message(errorcode)
            exc = UnrarException(errormessage)
        raise exc

    def _read_header(self):
        self._current_filename = None
        errorcode = self._unrar.RARReadHeaderEx(self._handle, ctypes.byref(self._headerdata))
        self._check_errorcode(errorcode)
        self._current_filename = self._headerdata.FileNameW

    def _process(self, dest=None):
        """Process current entry: extract or skip it"""
        if dest is None:
            mode = RarArchive._ProcessingMode.RAR_SKIP
        else:
            mode = RarArchive._ProcessingMode.RAR_EXTRACT
        errorcode = self._unrar.RARProcessFileW(self._handle, mode, None, dest)
        self._current_filename = None
        self._check_errorcode(errorcode)

    def _close(self):
        """Close the rar handle previously obtained by open"""
        if self._handle is None:
            return
        if (errorcode := self._unrar.RARCloseArchive(self._handle)) != 0:
            errormessage = UnrarException.get_error_message(errorcode)
            raise UnrarException(f'Could not close archive: {errormessage}')
        self._handle = None


class UnrarException(Exception):
    """Exception class for RarArchive"""
    _exceptions = {
        RarArchive._ErrorCode.ERAR_END_ARCHIVE: 'End of archive',
        RarArchive._ErrorCode.ERAR_NO_MEMORY: 'Not enough memory to initialize data structures',
        RarArchive._ErrorCode.ERAR_BAD_DATA: 'Bad data, CRC mismatch',
        RarArchive._ErrorCode.ERAR_BAD_ARCHIVE: 'Volume is not valid RAR archive',
        RarArchive._ErrorCode.ERAR_UNKNOWN_FORMAT: 'Unknown archive format',
        RarArchive._ErrorCode.ERAR_EOPEN: 'Volume open error',
        RarArchive._ErrorCode.ERAR_ECREATE: 'File create error',
        RarArchive._ErrorCode.ERAR_ECLOSE: 'File close error',
        RarArchive._ErrorCode.ERAR_EREAD: 'Read error',
        RarArchive._ErrorCode.ERAR_EWRITE: 'Write error',
        RarArchive._ErrorCode.ERAR_SMALL_BUF: 'Buffer too small',
        RarArchive._ErrorCode.ERAR_UNKNOWN: 'Unknown error',
        RarArchive._ErrorCode.ERAR_MISSING_PASSWORD: 'Password missing',
    }

    @staticmethod
    def get_error_message(errorcode):
        if errorcode in UnrarException._exceptions:
            return UnrarException._exceptions[errorcode]
        else:
            return 'Unkown error'


def _get_unrar():
    """Tries to load libunrar and will return a handle of it.
    Returns None if an error occured or the library couldn't be found"""
    global _unrar_dll
    if _unrar_dll is not None:
        return _unrar_dll

    # find_library on UNIX uses various mechanisms to determine the path
    # of a library, so one could assume the library is not installed
    # when find_library fails
    if unrar_path := ctypes.util.find_library('unrar'):
        try:
            _unrar_dll = ctypes.cdll.LoadLibrary(unrar_path)
            return _unrar_dll
        except OSError:
            pass
