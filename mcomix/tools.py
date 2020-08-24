# -*- coding: utf-8 -*-

"""tools.py - Contains various helper functions"""

from hashlib import sha256


def sha256str(s):
    return sha256(s.encode('utf8')).hexdigest()
