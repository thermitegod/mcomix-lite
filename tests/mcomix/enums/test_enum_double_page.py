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

from mcomix_compiled import DoublePage


def test_doublepage_never():
    assert DoublePage.NEVER == 0


def test_doublepage_title():
    assert DoublePage.AS_ONE_TITLE == 1


def test_doublepage_wide():
    assert DoublePage.AS_ONE_WIDE == 2


def test_doublepage_always():
    assert DoublePage.ALWAYS == 3
