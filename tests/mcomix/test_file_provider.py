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

from mcomix.file_provider import GetFileProvider, OrderedFileProvider, PreDefinedFileProvider


def test_file_provider_ordered():
    filelist = [Path('test_01.zip')]
    get_provider = GetFileProvider()
    provider = get_provider.get_file_provider(filelist)

    assert isinstance(provider, OrderedFileProvider)


def test_file_provider_predefined():
    filelist = [Path('test_01.zip'), Path('test_02.zip')]
    get_provider = GetFileProvider()
    provider = get_provider.get_file_provider(filelist)

    assert isinstance(provider, PreDefinedFileProvider)
