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

from mcomix.enums import FileSortType, FileSortDirection


def test_file_sort_none():
    assert FileSortType.NONE.value == 0


def test_file_sort_name():
    assert FileSortType.NAME.value == 1


def test_file_sort_size():
    assert FileSortType.SIZE.value == 2


def test_file_sort_last_mod():
    assert FileSortType.LAST_MODIFIED.value == 3


def test_file_sort_literal():
    assert FileSortType.NAME_LITERAL.value == 4


def test_file_sort_descending():
    assert FileSortDirection.DESCENDING.value == 0


def test_file_sort_ascending():
    assert FileSortDirection.ASCENDING.value == 1
