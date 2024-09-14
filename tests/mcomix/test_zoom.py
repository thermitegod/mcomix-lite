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

from mcomix.enums import ZoomModes

# from mcomix.fallback.zoom import ZoomModel

from mcomix_compiled import ZoomModel

# Best with stretching

def test_zoom__single_page__best_stretch():
    zoom = ZoomModel()
    zoom.set_fit_mode(ZoomModes.BEST.value)
    zoom.set_scale_up(True)
    zoom.reset_user_zoom()

    scaled_sizes = zoom.get_zoomed_size([[1454, 2062]], [2417, 1363], 0, [False])

    assert scaled_sizes == [[961, 1363]]

def test_zoom__double_page__best_stretch():
    zoom = ZoomModel()
    zoom.set_fit_mode(ZoomModes.BEST.value)
    zoom.set_scale_up(True)
    zoom.reset_user_zoom()

    scaled_sizes = zoom.get_zoomed_size([[1454, 2062], [1454, 2062]], [2417, 1363], 0, [False, False])

    assert scaled_sizes == [[961, 1363], [961, 1363]]

# Width with stretching

def test_zoom__single_page__width_stretch():
    zoom = ZoomModel()
    zoom.set_fit_mode(ZoomModes.WIDTH.value)
    zoom.set_scale_up(True)
    zoom.reset_user_zoom()

    scaled_sizes = zoom.get_zoomed_size([[1454, 2062]], [2417, 1363], 0, [False])

    assert scaled_sizes == [[2417, 3428]]

def test_zoom__double_page__width_stretch():
    zoom = ZoomModel()
    zoom.set_fit_mode(ZoomModes.WIDTH.value)
    zoom.set_scale_up(True)
    zoom.reset_user_zoom()

    scaled_sizes = zoom.get_zoomed_size([[1454, 2062], [1454, 2062]], [2417, 1363], 0, [False, False])

    assert scaled_sizes == [[1208, 1713], [1208, 1713]]

# Height with stretching

def test_zoom__single_page__height_stretch():
    zoom = ZoomModel()
    zoom.set_fit_mode(ZoomModes.HEIGHT.value)
    zoom.set_scale_up(True)
    zoom.reset_user_zoom()

    scaled_sizes = zoom.get_zoomed_size([[1454, 2062]], [2417, 1363], 0, [False])

    assert scaled_sizes == [[961, 1363]]

def test_zoom__double_page__height_stretch():
    zoom = ZoomModel()
    zoom.set_fit_mode(ZoomModes.HEIGHT.value)
    zoom.set_scale_up(True)
    zoom.reset_user_zoom()

    scaled_sizes = zoom.get_zoomed_size([[1454, 2062], [1454, 2062]], [2417, 1363], 0, [False, False])

    assert scaled_sizes == [[961, 1363], [961, 1363]]

# Manual with stretching

def test_zoom__single_page__manual_stretch():
    zoom = ZoomModel()
    zoom.set_fit_mode(ZoomModes.MANUAL.value)
    zoom.set_scale_up(True)
    zoom.reset_user_zoom()

    scaled_sizes = zoom.get_zoomed_size([[1454, 2062]], [2417, 1363], 0, [False])

    assert scaled_sizes == [[1454, 2062]]

def test_zoom__double_page__manual_stretch():
    zoom = ZoomModel()
    zoom.set_fit_mode(ZoomModes.MANUAL.value)
    zoom.set_scale_up(True)
    zoom.reset_user_zoom()

    scaled_sizes = zoom.get_zoomed_size([[1454, 2062], [1454, 2062]], [2417, 1363], 0, [False, False])

    assert scaled_sizes == [[1454, 2062], [1454, 2062]]

# Size with stretching

# TODO - need to pass config values for this to work right

#def test_zoom__single_page__size_stretch():
#    zoom = ZoomModel()
#    zoom.set_fit_mode(ZoomModes.SIZE.value)
#    zoom.set_scale_up(True)
#    zoom.reset_user_zoom()
#
#    scaled_sizes = zoom.get_zoomed_size([[1454, 2062]], [2417, 1363], 0, [False])
#
#    assert scaled_sizes == [[1269, 1800]]

#def test_zoom__double_page__size_stretch():
#    zoom = ZoomModel()
#    zoom.set_fit_mode(ZoomModes.SIZE.value)
#    zoom.set_scale_up(True)
#    zoom.reset_user_zoom()
#
#    scaled_sizes = zoom.get_zoomed_size([[1454, 2062], [1454, 2062]], [2417, 1363], 0, [False, False])
#
#    assert scaled_sizes == [[1269, 1800], [1269, 1800]]
