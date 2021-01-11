# -*- coding: utf-8 -*-

"""file_provider.py - Handles listing files for the current directory and
switching to the next/previous directory"""

import re

# Split into float, int, and characters
NUMERIC_REGEXP = re.compile(r'\d+[.]\d+|\d+|\D+')


class SortAlphanumeric:
    def __init__(self, filenames: list):
        """
        Do an in-place alphanumeric sort of the strings in <filenames>,
        such that for an example "1.jpg", "2.jpg", "10.jpg" is a sorted ordering
        """

        super().__init__()

        filenames.sort(key=self._keyfunc)

    @staticmethod
    def _isfloat(p):
        try:
            return 0, float(p)
        except ValueError:
            return 1, p.lower()

    def _keyfunc(self, s):
        x, y, z = str(s).rpartition('.')
        if z.isdigit():
            # extension with only digital is not extension
            x = f'{x}{y}{z}'
            z = ''
        return [self._isfloat(p) for p in (*NUMERIC_REGEXP.findall(x), z)]
