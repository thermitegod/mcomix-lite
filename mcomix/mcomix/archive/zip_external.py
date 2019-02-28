# -*- coding: utf-8 -*-

""" ZIP archive extractor via executable."""

from mcomix import i18n, process
from mcomix.archive import archive_base

# Filled on-demand by ZipArchive
_zip_executable = -1


class ZipArchive(archive_base.ExternalExecutableArchive):
    """ ZIP file extractor using unzip executable. """

    def _get_executable(self):
        return ZipArchive._find_unzip_executable()

    def _get_list_arguments(self):
        return ['-Z1']

    def _get_extract_arguments(self):
        return ['-p', '-P', '']

    @staticmethod
    def _find_unzip_executable():
        """ Tries to run unzip, and returns 'unzip' on success.
        Returns None on failure. """
        global _zip_executable
        if -1 == _zip_executable:
            _zip_executable = process.find_executable(('unzip',))
        return _zip_executable

    @staticmethod
    def is_available():
        return bool(ZipArchive._find_unzip_executable())

    def _unicode_filename(self, filename, conversion_func=i18n.to_unicode):
        unicode_name = conversion_func(filename)
        # As it turns out, unzip will try to interpret filenames as glob...
        for c in '[*?':
            filename = filename.replace(c, '[' + c + ']')

        filename = filename.replace('\\', '\\\\')
        self.unicode_mapping[unicode_name] = filename
        return unicode_name
