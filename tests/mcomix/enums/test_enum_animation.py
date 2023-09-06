from mcomix.enums import Animation


def test_animation_disabled():
    assert Animation.DISABLED.value == 0


def test_animation_normal():
    assert Animation.NORMAL.value == 1
