from mcomix.enums import ScalingGDK


def test_scaleing_gdk():
    for f in ScalingGDK:
        assert isinstance(f.value, int)
