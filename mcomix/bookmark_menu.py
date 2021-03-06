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

    def __init__(self, ui, window):
        super().__init__()

        self.__window = window

        self.__window.bookmark_backend.initialize(window)

        self.__actiongroup = Gtk.ActionGroup(name='mcomix-bookmarks')
        self.__actiongroup.add_actions([
            ('add_bookmark', 'mcomix-add-bookmark', 'Add _Bookmark',
             '<Control>D', None, self._add_current_to_bookmarks),
            ('edit_bookmarks', None, '_Edit Bookmarks...',
             '<Control>B', None, self._edit_bookmarks)])

        action = self.__actiongroup.get_action('add_bookmark')
        action.set_accel_group(ui.get_accel_group())
        self.__add_button = action.create_menu_item()
        self.append(self.__add_button)

        action = self.__actiongroup.get_action('edit_bookmarks')
        action.set_accel_group(ui.get_accel_group())
        self.__edit_button = action.create_menu_item()
        self.append(self.__edit_button)

        # Re-create the bookmarks menu if one was added/removed
        self._create_bookmark_menuitems()
        self.__window.bookmark_backend.add_bookmark += lambda bookmark: self._create_bookmark_menuitems()
        self.__window.bookmark_backend.remove_bookmark += lambda bookmark: self._create_bookmark_menuitems()

        self.show_all()

    def _create_bookmark_menuitems(self):
        # Delete all old menu entries
        for item in self.get_children():
            if item not in (self.__add_button, self.__edit_button):
                self.remove(item)

        # Add separator
        bookmarks = self.__window.bookmark_backend.get_bookmarks()
        if bookmarks:
            separator = Gtk.SeparatorMenuItem()
            separator.show()
            self.append(separator)

        # Add new bookmarks
        for bookmark in bookmarks:
            self.add_bookmark(bookmark)

    def add_bookmark(self, bookmark):
        """
        Add <bookmark> to the menu
        """

        bookmark = bookmark.clone()
        bookmark.show()
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

    def set_sensitive(self, loaded):
        """
        Set the sensitivities of menu items as appropriate if <loaded>
        represents whether a file is currently loaded in the main program or not
        """

        self.__actiongroup.get_action('add_bookmark').set_sensitive(loaded)
