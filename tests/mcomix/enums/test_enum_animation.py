# -*- coding: utf-8 -*-

from mcomix.enums.animation import Animation


def test_animation_disabled():
    assert Animation.DISABLED.value == 0


def test_animation_normal():
    assert Animation.NORMAL.value == 1


def test_animation_once():
    assert Animation.ONCE.value == 2


def test_animation_inf():
    assert Animation.INF.value == 3
