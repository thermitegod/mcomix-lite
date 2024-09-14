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

from mcomix.formats.image import ImageSupported


@pytest.mark.parametrize('image', [
    Path('test.jpeg'),
    Path('test.jpg'),
    Path('test.png'),

    # Path('test.ppm'),
    # Path('test.ppn'),
])
def test_is_archive(image: Path):
    assert ImageSupported.is_image_file(image)


@pytest.mark.parametrize('not_image', [
    Path('test.pdf'),  # make sure .pdf files are not detected as supported

    Path('test.not'),
    Path('test.an'),
    Path('test.image'),
    Path('test.file'),
])
def test_is_not_archive(not_image: Path):
    assert not ImageSupported.is_image_file(not_image)
