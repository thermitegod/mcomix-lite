# -*- coding: utf-8 -*-

from mcomix.enums.scroll import Scroll


def test_scroll_end():
    assert Scroll.END.value == -4


def test_scroll_start():
    assert Scroll.START.value == -3


def test_scroll_center():
    assert Scroll.CENTER.value == -2
