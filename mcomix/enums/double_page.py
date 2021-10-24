# -*- coding: utf-8 -*-

from enum import Enum


class DoublePage(Enum):
    NEVER = 0
    AS_ONE_TITLE = 1
    AS_ONE_WIDE = 2
    ALWAYS = 3
