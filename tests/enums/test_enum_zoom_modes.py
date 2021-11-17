# -*- coding: utf-8 -*-

from mcomix.enums.zoom_modes import ZoomModes, ZoomAxis


def test_zoom_modes_best():
    assert ZoomModes.BEST.value == 0


def test_zoom_modes_width():
    assert ZoomModes.WIDTH.value == 1


def test_zoom_modes_height():
    assert ZoomModes.HEIGHT.value == 2


def test_zoom_modes_manual():
    assert ZoomModes.MANUAL.value == 3


def test_zoom_modes_size():
    assert ZoomModes.SIZE.value == 4


def test_zoom_axis_distribution():
    assert ZoomAxis.DISTRIBUTION.value == 0


def test_zoom_axis_alignment():
    assert ZoomAxis.ALIGNMENT.value == 1


def test_zoom_axis_width():
    assert ZoomAxis.WIDTH.value == 0


def test_zoom_axis_height():
    assert ZoomAxis.HEIGHT.value == 1
