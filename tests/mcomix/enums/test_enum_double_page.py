from mcomix.enums import DoublePage


def test_doublepage_never():
    assert DoublePage.NEVER.value == 0


def test_doublepage_title():
    assert DoublePage.AS_ONE_TITLE.value == 1


def test_doublepage_wide():
    assert DoublePage.AS_ONE_WIDE.value == 2


def test_doublepage_always():
    assert DoublePage.ALWAYS.value == 3
