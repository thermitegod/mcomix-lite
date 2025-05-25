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

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from gi.repository import Gtk

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.gui.main_window import MainWindow


class Bookmark(Gtk.MenuItem):
    """
    Bookmark represents one bookmark. It extends the Gtk.MenuItem
    and is thus put directly in the bookmarks menu
    """

    def __init__(self, window: MainWindow, path: Path, current_page: int, total_pages: int, date_added: float):
        self.__window = window

        self.__name: str = path.name
        self.__path: Path = path
        self.__current_page: int = current_page
        self.__total_pages: int = total_pages
        self.__date_added: float = date_added

        self.__row_format = (
            self.__name,
            f'{self.__current_page} / {self.__total_pages}',
            str(self.__path),
            datetime.fromtimestamp(self.__date_added).strftime('%Y-%m-%d %H:%M:%S'),
            self
        )

        super().__init__(label=f'{self.__name}, ({self.__current_page} / {self.__total_pages})')

        self.connect('activate', self._open_bookmark)

    @property
    def bookmark_name(self):
        return self.__name

    @property
    def bookmark_path(self):
        return str(self.__path)

    @property
    def bookmark_current_page(self):
        return self.__current_page

    @property
    def bookmark_total_pages(self):
        return self.__total_pages

    @property
    def bookmark_date_added(self):
        return self.__date_added

    def _open_bookmark(self, *args):
        """
        Open the file and page the bookmark represents
        """

        self.__window.bookmark_backend.open_bookmark(path=self.__path, current_page=self.__current_page)

    def to_row(self):
        """
        Return a tuple corresponding to one row in the _BookmarkDialog's ListStore
        """

        return self.__row_format
