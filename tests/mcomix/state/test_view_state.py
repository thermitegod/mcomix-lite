# -*- coding: utf-8 -*-

import pytest
from mcomix.state.view_state import ViewState


@pytest.mark.parametrize('set,get', [
    (True, True),
    (False, False),
])
def test_view_state_manga(set: bool, get: bool):
    ViewState.is_manga_mode = set

    assert ViewState.is_manga_mode == get


@pytest.mark.parametrize('set,get', [
    (True, True),
    (False, False),
])
def test_view_state_double(set: bool, get: bool):
    ViewState.is_displaying_double = set

    assert ViewState.is_displaying_double == get
