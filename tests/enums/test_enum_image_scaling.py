# -*- coding: utf-8 -*-

from mcomix.enums.image_scaling import ScalingGDK, ScalingPIL


def test_scaleing_gdk():
    for f in ScalingGDK:
        assert isinstance(f.value, int)

def test_scaleing_pil():
    for f in ScalingPIL:
        assert isinstance(f.value, int)

