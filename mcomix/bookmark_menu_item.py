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

    def __init__(self, window, name, path, current_page, total_pages, date_added):
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

    def same_path(self, path: str):
        """
        Return True if the bookmark is for the file <path>
        """

        return Path(path) == Path(self.__path)

    def same_page(self, page):
        """
        Return True if the bookmark is for the same page
        """

        return page == self.__current_page

    def to_row(self):
        """
        Return a tuple corresponding to one row in the _BookmarkDialog's ListStore
        """

        page = f'{self.__current_page} / {self.__total_pages}'
        date = self.__date_added.strftime('%x %X')

        return self.__name, page, str(self.__path), date, self

    def pack(self):
        """
        Returns a dict. The bookmark can be fully
        re-created using the values in the dict
        """

        return {
            self.__name: {
                # YAML does not work with Pathlike objects
                'path': str(Path(self.__path).parent),
                'current_page': self.__current_page,
                'total_pages': self.__total_pages,
                # archive_type is deprecated, to be removed in next format change
                'archive_type': 0,
                'created': self.__date_added.timestamp()
            }
        }

    def __eq__(self, other):
        """
        Equality comparison for Bookmark items
        """

        if isinstance(other, Bookmark):
            return self.__path == other.__path and self.__current_page == other.__current_page

        return False

    def __hash__(self):
        """
        Hash for this object
        """

        return hash(self.__path) | hash(self.__current_page)
