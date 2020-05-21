# -*- coding: utf-8 -*-

"""tools.py - Contains various helper functions"""

import bisect
import gc
import math
import operator
import re
from functools import reduce
from hashlib import sha256
from os.path import splitext

NUMERIC_REGEXP = re.compile(r'\d+[.]\d+|\d+|\D+')  # Split into float, int, and characters
PREFIXED_BYTE_UNITS = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')


def alphanumeric_sort(filenames):
    """Do an in-place alphanumeric sort of the strings in <filenames>,
    such that for an example "1.jpg", "2.jpg", "10.jpg" is a sorted ordering"""
    def _isfloat(p):
        try:
            return 0, float(p)
        except ValueError:
            return 1, p.lower()

    def keyfunc(s):
        s, e = splitext(s)
        if e[1:].isdigit():  # extension with only digital is not extension
            s += e
            e = ''
        return [_isfloat(p) for p in (*NUMERIC_REGEXP.findall(s), e)]

    filenames.sort(key=keyfunc)


def bin_search(lst, value):
    """Binary search for sorted list C{lst}, looking for C{value}.
    @return: List index on success. On failure, it returns the 1's
    complement of the index where C{value} would be inserted.
    This implies that the return value is non-negative if and only if
    C{value} is contained in C{lst}"""
    if (index := bisect.bisect_left(lst, value)) != len(lst) and lst[index] == value:
        return index

    return ~index


def number_of_digits(n):
    if not n:
        return 1

    return int(math.log10(abs(n))) + 1


def format_byte_size(n):
    s = 0
    while n >= 1024:
        s += 1
        n /= 1024.0
    try:
        e = PREFIXED_BYTE_UNITS[s]
    except IndexError:
        e = f'C{s}i'
    return f'{n:.3f} {e}'


def garbage_collect():
    """Runs the garbage collector"""
    gc.collect(0)


def sha256str(s):
    return sha256(s.encode('utf8')).hexdigest()


def div(a, b):
    return float(a) / float(b)


def volume(t):
    return reduce(operator.mul, t, 1)


def relerr(approx, ideal):
    return abs(div(approx - ideal, ideal))


def smaller(a, b):
    """Returns a list with the i-th element set to True if and only the i-th
    element in a is less than the i-th element in b"""
    return map(operator.lt, a, b)


def scale(t, factor):
    return [x * factor for x in t]


def vector_sub(a, b):
    """Subtracts vector b from vector a"""
    return tuple(map(operator.sub, a, b))


def vector_opposite(a):
    """Returns the opposite vector -a"""
    return tuple(map(operator.neg, a))
