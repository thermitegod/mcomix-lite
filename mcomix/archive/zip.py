# -*- coding: utf-8 -*-

"""Unicode-aware wrapper for zipfile.ZipFile"""

import collections
import os
import threading
import zipfile

from mcomix import log
from mcomix.archive import archive_base


def is_py_supported_zipfile(path):
    """Check if a given zipfile has internal files stored with Python supported compression"""
    with zipfile.ZipFile(path, mode='r') as zip_file:
        for file_info in zip_file.infolist():
            try:
                descr = zipfile._get_decompressor(file_info.compress_type)
            except:
                return False
    return True


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
        destination_path = os.path.join(destination_dir, filename)
        info = self._contents_info[filename]
        with self._lock:
            data = self._zip.read(info)
        with self._create_file(destination_path) as new:
            filelen = new.write(data)

        if filelen != info.file_size:
            log.warning('%(filename)s\'s extracted size is %(actual_size)d bytes, but should '
                        'be %(expected_size)d bytes. The archive might be corrupt or in an unsupported format.',
                        {'filename': filename, 'actual_size': filelen,
                         'expected_size': info.file_size})

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
