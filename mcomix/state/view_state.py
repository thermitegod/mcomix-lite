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

from mcomix.preferences import config


class _ViewState:
    def __init__(self):
        super().__init__()

        self.__is_manga_mode: bool = config['DEFAULT_MANGA_MODE']
        self.__is_displaying_double: bool = False

    @property
    def is_manga_mode(self) -> bool:
        return self.__is_manga_mode

    @is_manga_mode.setter
    def is_manga_mode(self, value: bool) -> None:
        self.__is_manga_mode = value

    @property
    def is_displaying_double(self) -> bool:
        return self.__is_displaying_double

    @is_displaying_double.setter
    def is_displaying_double(self, value: bool) -> None:
        self.__is_displaying_double = value


ViewState = _ViewState()
