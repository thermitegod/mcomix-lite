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
        self._zip = zipfile.ZipFile(archive, 'r')
        self._lock = threading.Lock()

        # zipfile is usually not thread-safe
        # so use OrderedDict to save ZipInfo in order
        # {unicode_name: ZipInfo}
        self._contents_info = collections.OrderedDict()
        for info in self._zip.infolist():
            self._contents_info[info.filename] = info

        self.is_encrypted = self._has_encryption()
        self._password = None

    def is_solid(self):
        # zipfile is usually not thread-safe
        # so treat it as a solid archive to reduce seek operate
        return True

    def iter_contents(self):
        if self.is_encrypted and not self._password:
            self._get_password()
            self._zip.setpassword(self._password)
        yield from self._contents_info.keys()

    def extract(self, filename, destination_dir):
        with self._lock:
            data = self._zip.read(info := self._contents_info[filename])
        with self._create_file(destination_path := os.path.join(destination_dir, filename)) as new:
            filelen = new.write(data)

        if filelen != info.file_size:
            logger.warning(f'{filename}: extracted size is {filelen} bytes, but should be {info.file_size} bytes')

        return destination_path

    def close(self):
        self._zip.close()

    def _has_encryption(self):
        """Checks all files in the archive for encryption.
        Returns True if at least one encrypted file was found"""
        for info in self._contents_info.values():
            if info.flag_bits & 0x1:  # File is encrypted
                return True
        return False
