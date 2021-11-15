# -*- coding: utf-8 -*-

from mcomix.enums import PageOrientation


def test_page_orientation_manga():
    assert PageOrientation.MANGA.value == [-1, 1]


def test_page_orientation_western():
    assert PageOrientation.WESTERN.value == [1, 1]
