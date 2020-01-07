# -*- coding: utf-8 -*-

"""Unicode-aware wrapper for zipfile.ZipFile"""

import collections
import os
import threading
import zipfile

from loguru import logger

from mcomix.archive import archive_base


class ZipArchive(archive_base.BaseArchive):
    def __init__(self, archive):
        super(ZipArchive, self).__init__(archive)
        self.__zip = zipfile.ZipFile(archive, 'r')
        self.__lock = threading.Lock()

        # zipfile is usually not thread-safe
        # so use OrderedDict to save ZipInfo in order
        # {unicode_name: ZipInfo}
        self.__contents_info = collections.OrderedDict()
        for info in self.__zip.infolist():
            self.__contents_info[info.filename] = info

        self.__is_encrypted = self._has_encryption()
        self.__password = None

    def is_solid(self):
        # zipfile is usually not thread-safe
        # so treat it as a solid archive to reduce seek operate
        return True

    def iter_contents(self):
        if self.__is_encrypted and not self.__password:
            self._get_password()
            self.__zip.setpassword(self.__password)
        yield from self.__contents_info.keys()

    def extract(self, filename, destination_dir):
        with self.__lock:
            data = self.__zip.read(info := self.__contents_info[filename])
        with self._create_file(destination_path := os.path.join(destination_dir, filename)) as new:
            filelen = new.write(data)

        if filelen != info.file_size:
            logger.warning(f'{filename}: extracted size is {filelen} bytes, but should be {info.file_size} bytes')

        return destination_path

    def close(self):
        self.__zip.close()

    def _has_encryption(self):
        """Checks all files in the archive for encryption.
        Returns True if at least one encrypted file was found"""
        for info in self.__contents_info.values():
            if info.flag_bits & 0x1:  # File is encrypted
                return True
        return False
