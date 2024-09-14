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
# from mcomix.fallback.layout import Layout

from mcomix_compiled import Box
from mcomix_compiled import Layout

def test_layout_dummy():
    layout = Layout([[1, 1]], [1, 1], [1, 1], 0, 0)

    assert layout.get_content_boxes() == [Box([1, 1])]
    assert layout.get_orientation() == [1, 1]
    assert layout.get_union_box() == Box([1, 1])
    assert layout.get_viewport_box() == Box([1, 1])

def test_layout_single_page():
    layout = Layout([[961, 1363]], [2417, 1363], [1, 1], 0, 1)

    # Content Box
    assert len(layout.get_content_boxes()) == 1
    assert layout.get_content_boxes() == [Box([728, 0], [961, 1363])]
    assert layout.get_content_boxes()[0].get_size() == [961, 1363]
    assert layout.get_content_boxes()[0].get_position() == [728, 0]

    # Orientation
    assert layout.get_orientation() == [1, 1]

    # Union Box
    assert layout.get_union_box() == Box([2417, 1363])
    assert layout.get_union_box().get_size() == [2417, 1363]
    assert layout.get_union_box().get_position() == [0, 0]

    # Viewport Box
    assert layout.get_viewport_box() == Box([2417, 1363])
    assert layout.get_viewport_box().get_size() == [2417, 1363]
    assert layout.get_viewport_box().get_position() == [0, 0]

def test_layout_single_page_rect():
    layout = Layout([[1921, 1363]], [2417, 1363], [1, 1], 0, 1)

    # Content Box
    assert len(layout.get_content_boxes()) == 1
    assert layout.get_content_boxes() == [Box([248, 0], [1921, 1363])]
    assert layout.get_content_boxes()[0].get_size() == [1921, 1363]
    assert layout.get_content_boxes()[0].get_position() == [248, 0]

    # Orientation
    assert layout.get_orientation() == [1, 1]

    # Union Box
    assert layout.get_union_box() == Box([2417, 1363])
    assert layout.get_union_box().get_size() == [2417, 1363]
    assert layout.get_union_box().get_position() == [0, 0]

    # Viewport Box
    assert layout.get_viewport_box() == Box([2417, 1363])
    assert layout.get_viewport_box().get_size() == [2417, 1363]
    assert layout.get_viewport_box().get_position() == [0, 0]

def test_layout_double_page_manga():
    layout = Layout([[961, 1363], [961, 1363]], [2417, 1363], [-1, 1], 0, 1)

    # Content Box
    assert len(layout.get_content_boxes()) == 2
    assert layout.get_content_boxes() == [Box([1209, 0], [961, 1363]), Box([246, 0], [961, 1363])]
    assert layout.get_content_boxes()[0].get_size() == [961, 1363]
    assert layout.get_content_boxes()[0].get_position() == [1209, 0]
    assert layout.get_content_boxes()[1].get_size() == [961, 1363]
    assert layout.get_content_boxes()[1].get_position() == [246, 0]

    # Orientation
    assert layout.get_orientation() == [-1, 1]

    # Union Box
    assert layout.get_union_box() == Box([2417, 1363])
    assert layout.get_union_box().get_size() == [2417, 1363]
    assert layout.get_union_box().get_position() == [0, 0]

    # Viewport Box
    assert layout.get_viewport_box() == Box([2417, 1363])
    assert layout.get_viewport_box().get_size() == [2417, 1363]
    assert layout.get_viewport_box().get_position() == [0, 0]

def test_layout_double_page_western():
    layout = Layout([[961, 1363], [961, 1363]], [2417, 1363], [1, 1], 0, 1)

    # Content Box
    assert len(layout.get_content_boxes()) == 2
    assert layout.get_content_boxes() == [Box([247, 0], [961, 1363]), Box([1210, 0], [961, 1363])]
    assert layout.get_content_boxes()[0].get_size() == [961, 1363]
    assert layout.get_content_boxes()[0].get_position() == [247, 0]
    assert layout.get_content_boxes()[1].get_size() == [961, 1363]
    assert layout.get_content_boxes()[1].get_position() == [1210, 0]

    # Orientation
    assert layout.get_orientation() == [1, 1]

    # Union Box
    assert layout.get_union_box() == Box([2417, 1363])
    assert layout.get_union_box().get_size() == [2417, 1363]
    assert layout.get_union_box().get_position() == [0, 0]

    # Viewport Box
    assert layout.get_viewport_box() == Box([2417, 1363])
    assert layout.get_viewport_box().get_size() == [2417, 1363]
    assert layout.get_viewport_box().get_position() == [0, 0]
