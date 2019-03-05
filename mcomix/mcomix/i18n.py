# -*- coding: utf-8 -*-

import sys
from builtins import str

import chardet


def to_unicode(string):
    """Convert <string> to unicode. First try the default filesystem
    encoding, and then fall back on some common encodings"""
    if isinstance(string, str):
        return string

    for encoding in (chardet.detect(string)['encoding'], sys.getfilesystemencoding()):
        return str(string, encoding)


def to_utf8(string):
    """Helper function that converts unicode objects to UTF-8 encoded
    strings. Non-unicode strings are assumed to be already encoded
    and returned as-is"""
    if isinstance(string, str):
        return string.encode('utf-8')
    else:
        return string
