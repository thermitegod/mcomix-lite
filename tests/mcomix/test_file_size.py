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

from pathlib import Path

from mcomix.file_size import format_filesize
from mcomix.preferences import config

def test_file_size():
    config['SI_UNITS'] = False
    test_file = Path(__file__).parent.parent.parent / 'COPYING'
    assert format_filesize(test_file) == '17.814 KiB'


# def test_file_size_si():
#     config['SI_UNITS'] = True
#     test_file = Path(__file__).parent.parent.parent / 'COPYING'
#     assert format_filesize(test_file) == '18.242 KB'
