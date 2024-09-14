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

from mcomix.formats.archive import ArchiveSupported


@pytest.mark.parametrize('archive', [
    Path('test.zip'),
    Path('test.cbz'),

    Path('test.rar'),
    Path('test.cbr'),

    Path('test.7z'),
    Path('test.cb7'),

    Path('test.tar'),
    Path('test.cbt'),

    Path('test.tar.gz'),
    Path('test.tar.bz2'),
    Path('test.tar.lzma'),
    Path('test.tar.xz'),
    Path('test.tar.lz4'),
    Path('test.tar.zst'),

    Path('test.lrzip'),
    Path('test.lzip'),

    Path('test.lha'),
    Path('test.lzh'),
])
def test_is_archive(archive: Path):
    assert ArchiveSupported.is_archive_file(archive)


@pytest.mark.parametrize('not_archive', [
    (Path('test.not')),
    (Path('test.an')),
    (Path('test.archive')),
    (Path('test.file')),

])
def test_is_not_archive(not_archive: Path):
    assert not ArchiveSupported.is_archive_file(not_archive)
