# -*- coding: utf-8 -*-

"""bookmark_backend.py - Bookmarks handler"""

import datetime
import os
import pickle
import time

from gi.repository import Gtk

from mcomix import bookmark_menu_item, callback, constants, log, message_dialog


class __BookmarksStore(object):
    """The _BookmarksStore is a backend for both the bookmarks menu and dialog.
    Changes in the _BookmarksStore are mirrored in both"""

    def __init__(self):
        self._initialized = False
        self._window = None
        self._file_handler = None
        self._image_handler = None

        bookmarks, mtime = self.load_bookmarks()

        #: List of bookmarks
        self._bookmarks = bookmarks
        #: Modification date of bookmarks file
        self._bookmarks_mtime = mtime

    def initialize(self, window):
        """Initializes references to the main window and file/image handlers"""
        if not self._initialized:
            self._window = window
            self._file_handler = window.filehandler
            self._image_handler = window.imagehandler
            self._initialized = True

            # Update already loaded bookmarks with window and file handler information
            for bookmark in self._bookmarks:
                bookmark._window = window
                bookmark._file_handler = window.filehandler

    def add_bookmark_by_values(self, name, path, page, numpages, archive_type, date_added):
        """Create a bookmark and add it to the list"""
        bookmark = bookmark_menu_item._Bookmark(self._window, self._file_handler,
                                                name, path, page, numpages, archive_type, date_added)

        self.add_bookmark(bookmark)

    @callback.Callback
    def add_bookmark(self, bookmark):
        """Add the <bookmark> to the list"""
        self._bookmarks.append(bookmark)
        self.write_bookmarks_file()

    @callback.Callback
    def remove_bookmark(self, bookmark):
        """Remove the <bookmark> from the list"""
        self._bookmarks.remove(bookmark)
        self.write_bookmarks_file()

    def add_current_to_bookmarks(self):
        """Add the currently viewed page to the list"""
        name = self._image_handler.get_pretty_current_filename()
        path = self._image_handler.get_real_path()
        page = self._image_handler.get_current_page()
        numpages = self._image_handler.get_number_of_pages()
        archive_type = self._file_handler.archive_type
        date_added = datetime.datetime.now()

        same_file_bookmarks = []

        for bookmark in self._bookmarks:
            if bookmark.same_path(path):
                if bookmark.same_page(page):
                    # Do not create identical bookmarks
                    return
                else:
                    same_file_bookmarks.append(bookmark)

        # If the same file was already bookmarked, ask to replace
        # the existing bookmarks before deleting them.
        if len(same_file_bookmarks) > 0:
            response = self.show_replace_bookmark_dialog(same_file_bookmarks, page)

            # Delete old bookmarks
            if response == Gtk.ResponseType.YES:
                for bookmark in same_file_bookmarks:
                    self.remove_bookmark(bookmark)
            # Perform no action
            elif response not in (Gtk.ResponseType.YES, Gtk.ResponseType.NO):
                return

        self.add_bookmark_by_values(name, path, page, numpages, archive_type, date_added)

    def get_bookmarks(self):
        """Return all the bookmarks in the list"""
        if not self.file_was_modified():
            return self._bookmarks
        else:
            self._bookmarks, self._bookmarks_mtime = self.load_bookmarks()
            return self._bookmarks

    def load_bookmarks(self):
        """Loads persisted bookmarks from a local file.
        @return: Tuple of (bookmarks, file mtime)"""
        path = constants.BOOKMARK_PATH
        bookmarks = []
        mtime = 0

        if os.path.isfile(path):
            try:
                mtime = os.stat(path).st_mtime
                with open(path, 'rb') as fd:
                    version = pickle.load(fd)
                    packs = pickle.load(fd)

                    for pack in packs:
                        bookmark = bookmark_menu_item._Bookmark(self._window, self._file_handler, *pack)
                        bookmarks.append(bookmark)

            except Exception:
                log.error(f'Could not parse bookmarks file {path}')

        return bookmarks, mtime

    def file_was_modified(self):
        """Checks the bookmark store's mtime to see if it has been modified
        since it was last read"""
        path = constants.BOOKMARK_PATH
        if os.path.isfile(path):
            try:
                mtime = os.stat(path).st_mtime
            except IOError:
                mtime = 0

            if mtime > self._bookmarks_mtime:
                return True
            else:
                return False
        else:
            return True

    def write_bookmarks_file(self):
        """Store relevant bookmark info in the mcomix directory"""
        # Merge changes in case file was modified from within other instances

        if self.file_was_modified():
            new_bookmarks, _ = self.load_bookmarks()
            self._bookmarks = list(set(self._bookmarks + new_bookmarks))

        with open(constants.BOOKMARK_PATH, 'wb') as fd:
            pickle.dump(constants.VERSION, fd, pickle.HIGHEST_PROTOCOL)

            packs = [bookmark.pack() for bookmark in self._bookmarks]
            pickle.dump(packs, fd, pickle.HIGHEST_PROTOCOL)

        self._bookmarks_mtime = time.time()

    def show_replace_bookmark_dialog(self, old_bookmarks, new_page):
        """Present a confirmation dialog to replace old bookmarks.
        @return RESPONSE_YES to create replace bookmarks,
        RESPONSE_NO to create a new bookmark, RESPONSE_CANCEL to abort creating
        a new bookmark"""
        dialog = message_dialog.MessageDialog(
                self._window,
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.NONE)
        dialog.add_buttons(
                Gtk.STOCK_YES, Gtk.ResponseType.YES,
                Gtk.STOCK_NO, Gtk.ResponseType.NO,
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.set_default_response(Gtk.ResponseType.YES)
        dialog.set_should_remember_choice('replace-existing-bookmark', (Gtk.ResponseType.YES, Gtk.ResponseType.NO))

        dialog.set_text(
                'The current book already contains marked pages.'
                f'Do you want to replace them with a new bookmark on page {new_page}? \n\n '
                'Selecting "No" will create a new bookmark.')

        return dialog.run()


# Singleton instance of the bookmarks store.
BookmarksStore = __BookmarksStore()
