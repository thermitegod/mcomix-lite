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

from mcomix_compiled import ZoomModes, ZoomAxis


def test_zoom_modes_best():
    assert ZoomModes.BEST == 0


def test_zoom_modes_width():
    assert ZoomModes.WIDTH == 1


def test_zoom_modes_height():
    assert ZoomModes.HEIGHT == 2


def test_zoom_modes_manual():
    assert ZoomModes.MANUAL == 3


def test_zoom_modes_size():
    assert ZoomModes.SIZE == 4


def test_zoom_axis_distribution():
    assert ZoomAxis.DISTRIBUTION == 0


def test_zoom_axis_alignment():
    assert ZoomAxis.ALIGNMENT == 1


def test_zoom_axis_width():
    assert ZoomAxis.WIDTH == 0


def test_zoom_axis_height():
    assert ZoomAxis.HEIGHT == 1
