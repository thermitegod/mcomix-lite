# -*- coding: utf-8 -*-

from enum import Enum


class FileSortType(Enum):
    NONE = 0
    NAME = 1
    SIZE = 2
    LAST_MODIFIED = 3
    NAME_LITERAL = 4


class FileSortDirection(Enum):
    DESCENDING = 0
    ASCENDING = 1
