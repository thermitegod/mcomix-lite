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

from mcomix_compiled import FileSortDirection, FileSortType


def test_file_sort_none():
    assert FileSortType.NONE == 0


def test_file_sort_name():
    assert FileSortType.NAME == 1


def test_file_sort_size():
    assert FileSortType.SIZE == 2


def test_file_sort_last_mod():
    assert FileSortType.LAST_MODIFIED == 3


def test_file_sort_literal():
    assert FileSortType.NAME_LITERAL == 4


def test_file_sort_descending():
    assert FileSortDirection.DESCENDING == 0


def test_file_sort_ascending():
    assert FileSortDirection.ASCENDING == 1
