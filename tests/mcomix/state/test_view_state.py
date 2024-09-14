# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

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
