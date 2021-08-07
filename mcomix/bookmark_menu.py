# -*- coding: utf-8 -*-

"""bookmark_menu.py - Bookmarks menu"""

from gi.repository import Gtk
from loguru import logger

from mcomix.bookmark_dialog import BookmarksDialog


class BookmarksMenu(Gtk.Menu):
    """
    BookmarksMenu extends Gtk.Menu with convenience methods relating to
    bookmarks. It contains fixed items for adding bookmarks etc. as well
    as dynamic items corresponding to the current bookmarks
    """

    def __init__(self, window):
        super().__init__()

        self.__window = window

        self.__window.bookmark_backend.initialize(window)

        item = Gtk.MenuItem()
        item.set_label('Add Bookmark')
        item.connect('activate', self._add_current_to_bookmarks)
        self.append(item)

        item = Gtk.MenuItem()
        item.set_label('Edit Bookmarks')
        item.connect('activate', self._edit_bookmarks)
        self.append(item)

        separator = Gtk.SeparatorMenuItem()
        self.append(separator)

        # Re-create the bookmarks menu if one was added/removed
        self._create_bookmark_menuitems()
        self.__window.bookmark_backend.add_bookmark += lambda bookmark: self._create_bookmark_menuitems()
        self.__window.bookmark_backend.remove_bookmark += lambda bookmark: self._create_bookmark_menuitems()

        self.show_all()

    def _create_bookmark_menuitems(self):
        # Delete all old menu entries
        for idx, item in enumerate(self.get_children()):
            # do not remove add/edit/sep
            if idx > 2:
                self.remove(item)

        # Add new bookmarks
        bookmarks = self.__window.bookmark_backend.get_bookmarks()
        for bookmark in bookmarks:
            self.add_bookmark(bookmark)

        self.show_all()

    def add_bookmark(self, bookmark):
        """
        Add <bookmark> to the menu
        """

        self.insert(bookmark, 3)

    def _add_current_to_bookmarks(self, *args):
        """
        Add the current page to the bookmarks list
        """

        try:
            self.__window.bookmark_backend.add_current_to_bookmarks()
        except TypeError:
            logger.warning('No file to add to bookmarks')

    def _edit_bookmarks(self, *args):
        """
        Open the bookmarks dialog
        """

        BookmarksDialog(self.__window, self.__window.bookmark_backend)
