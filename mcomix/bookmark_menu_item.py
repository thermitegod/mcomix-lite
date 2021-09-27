# -*- coding: utf-8 -*-

"""bookmark_menu_item.py - A signle bookmark item"""

from datetime import datetime
from pathlib import Path

from gi.repository import Gtk


class Bookmark(Gtk.MenuItem):
    """
    Bookmark represents one bookmark. It extends the Gtk.MenuItem
    and is thus put directly in the bookmarks menu
    """

    def __init__(self, window, name: str, path: Path, current_page: int, total_pages: int, date_added: float):
        self.__window = window

        self.__name = name
        self.__path = path
        self.__current_page = current_page
        self.__total_pages = total_pages
        self.__date_added = datetime.fromtimestamp(date_added)

        super().__init__(label=str(self), use_underline=False)

        self.connect('activate', self._open_bookmark)

    def __str__(self):
        return f'{self.__name}, ({self.__current_page} / {self.__total_pages})'

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

        page = f'{self.__current_page} / {self.__total_pages}'
        date = self.__date_added.strftime('%x %X')

        return self.__name, page, str(self.__path), date, self
