# -*- coding: utf-8 -*-

"""Glue around libunrar.so to extract RAR files without having to
resort to calling rar/unrar manually"""

import ctypes
import ctypes.util
from pathlib import Path

from loguru import logger

from mcomix.archive import archive_base

UNRARCALLBACK = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_uint, ctypes.c_long, ctypes.c_long, ctypes.c_long)


class RarArchive(archive_base.BaseArchive):
    """
    Wrapper class for libunrar. All string values passed to this class must be unicode objects.
    In turn, all values returned are also unicode
    """

    # Nope! Not a good idea...
    support_concurrent_extractions = False

    class _OpenMode:
        """
        Rar open mode
        """

        RAR_OM_EXTRACT = 1

    class _ProcessingMode:
        """
        Rar file processing mode
        """

        RAR_SKIP = 0
        RAR_EXTRACT = 2

    class ErrorCode:
        """
        Rar error codes
        """

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
        """
        Archive header structure. Used by DLL calls
        """

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
        """
        Archive file structure. Used by DLL calls
        """

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
        """
        Returns True if unrar.dll can be found, False otherwise

        :returns: will return whether unrar is available
        :rtype: bool
        """

        return bool(RarExecutable.find_unrar())

    def __init__(self, archive: str):
        super().__init__(archive)
        self.__unrar = RarExecutable.find_unrar()
        self.__handle = None
        self.__is_solid = False
        # Information about the current file will be stored in this structure
        self.__headerdata = RarArchive._RARHeaderDataEx()
        self.__current_filename = None

        # Set up function prototypes.
        # Mandatory since pointers get truncated on x64 otherwise!
        self.__unrar.RAROpenArchiveEx.restype = ctypes.c_void_p
        self.__unrar.RAROpenArchiveEx.argtypes = [ctypes.POINTER(RarArchive._RAROpenArchiveDataEx)]
        self.__unrar.RARCloseArchive.restype = ctypes.c_int
        self.__unrar.RARCloseArchive.argtypes = [ctypes.c_void_p]
        self.__unrar.RARReadHeaderEx.restype = ctypes.c_int
        self.__unrar.RARReadHeaderEx.argtypes = [ctypes.c_void_p, ctypes.POINTER(RarArchive._RARHeaderDataEx)]
        self.__unrar.RARProcessFileW.restype = ctypes.c_int
        self.__unrar.RARProcessFileW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p, ctypes.c_wchar_p]
        self.__unrar.RARSetCallback.argtypes = [ctypes.c_void_p, UNRARCALLBACK, ctypes.c_long]

    def is_solid(self):
        """
        Check if the archive is solid

        :return: whether the archive is solid
        :rtype: bool
        """

        return self.__is_solid

    def iter_contents(self):
        """
        List archive contents
        """

        self._close()
        self._open()
        try:
            while 1:
                self._read_header()
                if (0x10 & self.__headerdata.Flags) != 0:
                    self.__is_solid = True
                filename = self.__current_filename
                yield filename
                # Skip to the next entry if we're still on the same name
                # (extract may have been called by iter_extract).
                if filename == self.__current_filename:
                    self._process()
        except UnrarException as ex:
            logger.error(f'Error while listing contents: {str(ex)}')
        except EOFError:
            # End of archive reached
            pass
        finally:
            self._close()

    def extract(self, filename: str, destination_dir: Path):
        """
        Extract <filename> from the archive to <destination_dir>

        :param filename: file to extract
        :type filename: str
        :param destination_dir: extraction path
        :type destination_dir: Path
        :returns: full path of the extracted file
        :rtype: Path
        """

        if not self.__handle:
            self._open()
        destination_path = Path() / destination_dir / filename
        while 1:
            # Check if the current entry matches the requested file.
            if self.__current_filename is not None:
                if self.__current_filename == filename:
                    # It's the entry we're looking for, extract it.
                    dest = ctypes.c_wchar_p(str(destination_path))
                    self._process(dest)
                    break
                # Not the right entry, skip it.
                self._process()
            try:
                self._read_header()
            except EOFError:
                # Archive end was reached, this might be due to out-of-order
                # extraction while the handle was still open.
                logger.error('End of archive reached')
                break

        # After the method returns, the RAR handler is still open and pointing
        # to the next archive file. This will improve extraction speed for sequential file reads.
        # After all files have been extracted, close() should be called to free the handler resources.
        return destination_path

    def close(self):
        """
        Close the archive handle
        """

        self._close()

    def _open(self):
        """
        Open rar handle for extraction
        """

        archivedata = RarArchive._RAROpenArchiveDataEx(ArcNameW=self.archive,
                                                       OpenMode=RarArchive._OpenMode.RAR_OM_EXTRACT,
                                                       UserData=0)

        if not (handle := self.__unrar.RAROpenArchiveEx(ctypes.byref(archivedata))):
            errormessage = UnrarException.get_error_message(archivedata.OpenResult)
            raise UnrarException(f'Could not open archive: {errormessage}')
        self.__handle = handle

    def _check_errorcode(self, errorcode: int):
        """
        Check rar error code to see if any exceptions should be raised

        :param errorcode: rar error code
        :type errorcode: int
        """

        if not errorcode:
            # No error.
            return
        self._close()
        if RarArchive.ErrorCode.ERAR_END_ARCHIVE == errorcode:
            # End of archive reached.
            exc = EOFError()
        else:
            errormessage = UnrarException.get_error_message(errorcode)
            exc = UnrarException(errormessage)
        raise exc

    def _read_header(self):
        self.__current_filename = None
        errorcode = self.__unrar.RARReadHeaderEx(self.__handle, ctypes.byref(self.__headerdata))
        self._check_errorcode(errorcode)
        self.__current_filename = self.__headerdata.FileNameW

    def _process(self, dest=None):
        """
        Process current entry: extract or skip it
        """

        if dest is None:
            mode = RarArchive._ProcessingMode.RAR_SKIP
        else:
            mode = RarArchive._ProcessingMode.RAR_EXTRACT
        errorcode = self.__unrar.RARProcessFileW(self.__handle, mode, None, dest)
        self.__current_filename = None
        self._check_errorcode(errorcode)

    def _close(self):
        """
        Close the rar handle previously obtained by open
        """

        if self.__handle is None:
            return
        if (errorcode := self.__unrar.RARCloseArchive(self.__handle)) != 0:
            errormessage = UnrarException.get_error_message(errorcode)
            raise UnrarException(f'Could not close archive: {errormessage}')
        self.__handle = None


class UnrarException(Exception):
    """
    Exception class for RarArchive
    """

    _exceptions = {
        RarArchive.ErrorCode.ERAR_END_ARCHIVE: 'End of archive',
        RarArchive.ErrorCode.ERAR_NO_MEMORY: 'Not enough memory to initialize data structures',
        RarArchive.ErrorCode.ERAR_BAD_DATA: 'Bad data, CRC mismatch',
        RarArchive.ErrorCode.ERAR_BAD_ARCHIVE: 'Volume is not valid RAR archive',
        RarArchive.ErrorCode.ERAR_UNKNOWN_FORMAT: 'Unknown archive format',
        RarArchive.ErrorCode.ERAR_EOPEN: 'Volume open error',
        RarArchive.ErrorCode.ERAR_ECREATE: 'File create error',
        RarArchive.ErrorCode.ERAR_ECLOSE: 'File close error',
        RarArchive.ErrorCode.ERAR_EREAD: 'Read error',
        RarArchive.ErrorCode.ERAR_EWRITE: 'Write error',
        RarArchive.ErrorCode.ERAR_SMALL_BUF: 'Buffer too small',
        RarArchive.ErrorCode.ERAR_UNKNOWN: 'Unknown error',
        RarArchive.ErrorCode.ERAR_MISSING_PASSWORD: 'Password missing',
    }

    @staticmethod
    def get_error_message(errorcode):
        if errorcode in UnrarException._exceptions:
            return UnrarException._exceptions[errorcode]

        return 'Unkown error'


class _RarExecutable:
    def __init__(self):
        self.__unrar = None

    def find_unrar(self):
        """
        Tries to load libunrar and will return a handle of it.
        Returns None if an error occured or the library couldn't be found

        :returns: loaded unrar library
        """

        if self.__unrar is None:
            unrar = ctypes.util.find_library('unrar')
            if unrar is None:
                logger.error(f'failed to find unrar library')
                return None
            self.__unrar = ctypes.cdll.LoadLibrary(unrar)
        return self.__unrar


# Singleton instance
RarExecutable = _RarExecutable()
