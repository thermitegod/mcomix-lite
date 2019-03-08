# -*- coding: utf-8 -*-

""" LHA archive extractor. """

import re
import shutil

from mcomix.archive import archive_base

# Filled on-demand by LhaArchive
_lha_executable = -1


class LhaArchive(archive_base.ExternalExecutableArchive):
    """ LHA file extractor using the lha executable. """

    def _get_executable(self):
        return LhaArchive._find_lha_executable()

    def _get_list_arguments(self):
        return ['l', '-g', '-q2']

    def _get_extract_arguments(self):
        return ['p', '-q2']

    def _parse_list_output_line(self, line):
        match = re.search(r'\[generic\]\s+\d+\s+\S+?\s+\w+\s+\d+\s+\d+\s+(.+)$', line)
        if match:
            return match.group(1)
        else:
            return None

    @staticmethod
    def _find_lha_executable():
        """ Tries to start lha, and returns either 'lha' if
        it was started successfully or None otherwise. """
        exe = shutil.which('lha')
        if exe:
            return exe
        return None


    @staticmethod
    def is_available():
        return bool(LhaArchive._find_lha_executable())
