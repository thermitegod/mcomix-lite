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

from mcomix.sort.sort_alphanumeric import SortAlphanumeric


@pytest.mark.parametrize('unsorted_file_list,sorted_file_list', [
    ([], []),  # test empty
    ([9, 8, 7, 6, 5, 4, 3, 2, 1, 0], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),  # 1..9
    ([10.5, 10, 11, 1], [1, 10, 10.5, 11]),  # test 10.5 gets sorted correctly

    # all paths should be Pathlike objects, still check strings anyway
    (['test_01.png', 'test_10.png', 'test_5.png'], ['test_01.png', 'test_5.png', 'test_10.png']),
    (['test_01.png', 'test_02.png', 'test_01.5.png'], ['test_01.png', 'test_01.5.png', 'test_02.png']),
    (['test_01_test.png', 'test_02_test.png', 'test_01.5_test.png'], ['test_01_test.png', 'test_01.5_test.png', 'test_02_test.png']),

    # test Pathlike objects
    ([Path('test_01.png'), Path('test_10.png'), Path('test_05.png')], [Path('test_01.png'), Path('test_05.png'), Path('test_10.png')]),
    ([Path('test_01.png'), Path('test_02.png'), Path('test_01.5.png')], [Path('test_01.png'), Path('test_01.5.png'), Path('test_02.png')]),
])
def test_sort_alphanumeric(unsorted_file_list: list, sorted_file_list: list):

    SortAlphanumeric(unsorted_file_list)

    assert unsorted_file_list == sorted_file_list
