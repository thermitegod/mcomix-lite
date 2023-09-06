# -*- coding: utf-8 -*-

"""bookmark_menu_item.py - A signle bookmark item"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from gi.repository import Gtk

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class Bookmark(Gtk.MenuItem):
    """
    Bookmark represents one bookmark. It extends the Gtk.MenuItem
    and is thus put directly in the bookmarks menu
    """

    def __init__(self, window: MainWindow, path: Path, current_page: int, total_pages: int, date_added: float):
        self.__window = window

        self.__name = path.name
        self.__path = path
        self.__current_page = current_page
        self.__total_pages = total_pages
        self.__date_added = date_added

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
