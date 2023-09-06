from enum import Enum


class PageOrientation(Enum):
    MANGA = [-1, 1]   # R->L
    WESTERN = [1, 1]  # L->R
