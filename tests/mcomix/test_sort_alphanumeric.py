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
from pathlib import Path

try:
    from mcomix_compiled import sort_alphanumeric
except ImportError:
    from mcomix.fallback.sort import sort_alphanumeric


@pytest.mark.parametrize('unsorted_file_list,sorted_file_list', [
    ([Path('test_01.png'), Path('test_10.png'), Path('test_05.png')], [Path('test_01.png'), Path('test_05.png'), Path('test_10.png')]),
    ([Path('test_01.png'), Path('test_02.png'), Path('test_01.5.png')], [Path('test_01.png'), Path('test_01.5.png'), Path('test_02.png')]),
])
def test_sort_alphanumeric(unsorted_file_list: list[Path], sorted_file_list: list[Path]):

    unsorted_file_list = sort_alphanumeric(unsorted_file_list)

    assert unsorted_file_list == sorted_file_list
