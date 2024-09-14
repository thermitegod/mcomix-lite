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

# from mcomix.fallback.box import Box

from mcomix_compiled import Box

def test_box_equal_empty():
    box1 = Box()
    box2 = Box()
    assert box1 == box2

def test_box_equal():
    box1 = Box([2417, 1363])
    box2 = Box([2417, 1363])
    assert box1 == box2

def test_box_test01():
    box = Box([2417, 1363])

    assert box.get_position() == [0, 0]
    assert box.get_size() == [2417, 1363]

    box.set_position((0, 0))

    assert box.get_position() == [0, 0]
    assert box.get_size() == [2417, 1363]
