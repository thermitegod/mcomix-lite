# -*- coding: utf-8 -*-

from enum import Enum


class ZoomModes(Enum):
    BEST = 0
    WIDTH = 1
    HEIGHT = 2
    MANUAL = 3
    SIZE = 4


class ZoomAxis(Enum):
    DISTRIBUTION = 0
    ALIGNMENT = 1
    WIDTH = 0
    HEIGHT = 1
