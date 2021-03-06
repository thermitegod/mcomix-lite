# -*- coding: utf-8 -*-

"""bookmark_backend.py - Bookmarks handler"""

import time
from pathlib import Path

import yaml
from gi.repository import Gtk
from loguru import logger

from mcomix.bookmark_menu_item import Bookmark
from mcomix.constants import Constants
from mcomix.lib.callback import Callback
from mcomix.message_dialog import MessageDialog


class BookmarkBackend:
    """
    The _BookmarkBackend is a backend for both the bookmarks menu and dialog.
    Changes in the _BookmarkBackend are mirrored in both
    """

    def __init__(self):
        super().__init__()

        self.__initialized = False
        self.__window = None
        self.__file_handler = None
        self.__image_handler = None

        self.__bookmark_path = Constants.CONFIG_FILES['BOOKMARK']
        self.__bookmark_state = {'dirty': False}

        #: List of bookmarks
        self.__bookmarks = self.load_bookmarks_file()
        #: Modification date of bookmarks file
        self.__bookmarks_mtime = self.get_bookmarks_file_mtime()

    def initialize(self, window):
        """
        Initializes references to the main window and file/image handlers
        """

        if not self.__initialized:
            self.__window = window
            self.__file_handler = window.filehandler
            self.__image_handler = window.imagehandler
            self.__initialized = True

            # Update already loaded bookmarks with window and file handler information
            for bookmark in self.__bookmarks:
                bookmark.__window = window
                bookmark._file_handler = window.filehandler

    @Callback
    def add_bookmark(self, bookmark):
        """
        Add the <bookmark> to the list
        """

        self.__bookmarks.append(bookmark)

        self.__bookmark_state['dirty'] = True
        self.write_bookmarks_file()
        self.__bookmark_state['dirty'] = False

    @Callback
    def remove_bookmark(self, bookmark):
        """
        Remove the <bookmark> from the list
        """

        self.__bookmarks.remove(bookmark)

        self.__bookmark_state['dirty'] = True
        self.write_bookmarks_file()
        self.__bookmark_state['dirty'] = False

    def add_current_to_bookmarks(self):
        """
        Add the currently viewed page to the list
        """

        name = self.__image_handler.get_current_filename()
        path = self.__image_handler.get_real_path()
        page = self.__image_handler.get_current_page()
        numpages = self.__image_handler.get_number_of_pages()
        archive_type = self.__file_handler.get_archive_type()
        epoch = time.time()

        same_file_bookmarks = []

        for bookmark in self.__bookmarks:
            if bookmark.same_path(path):
                if bookmark.same_page(page):
                    logger.info(f'Bookmark already exists for \'{name}\' on page \'{page}\'')
                    return

                same_file_bookmarks.append(bookmark)

        # If the same file was already bookmarked, ask to replace
        # the existing bookmarks before deleting them.
        if len(same_file_bookmarks) > 0:
            response = self.show_replace_bookmark_dialog(page)

            # Delete old bookmarks
            if response == Gtk.ResponseType.YES:
                for bookmark in same_file_bookmarks:
                    self.remove_bookmark(bookmark)
            # Perform no action
            elif response not in (Gtk.ResponseType.YES, Gtk.ResponseType.NO):
                return

        bookmark = Bookmark(self.__window, self.__file_handler,
                            name, path, page, numpages, archive_type, epoch)
        self.add_bookmark(bookmark)

    def get_bookmarks(self):
        """
        Return all the bookmarks in the list
        """

        if not self.file_was_modified():
            return self.__bookmarks

        self.__bookmarks = self.load_bookmarks_file()
        return self.__bookmarks

    def get_bookmarks_file_mtime(self):
        if Path.is_file(self.__bookmark_path):
            return Path.stat(self.__bookmark_path).st_mtime
        return 0

    def load_bookmarks_file(self):
        """
        Loads persisted bookmarks from a local file.

        :return: Tuple of (bookmarks, file mtime)
        """

        bookmarks = []

        if Path.is_file(self.__bookmark_path):
            try:
                with Path.open(self.__bookmark_path, mode='rt', encoding='utf8') as fd:
                    packs = yaml.safe_load(fd)

                    for bookmark in packs:
                        for idx, item in enumerate(bookmark):
                            path = str(Path(bookmark[item]['path'], item))
                            current_page = bookmark[item]['current_page']
                            total_pages = bookmark[item]['total_pages']
                            archive_type = bookmark[item]['archive_type']
                            created = bookmark[item]['created']

                            bookmarks.append(Bookmark(self.__window, self.__file_handler,
                                                      name=item, path=path, page=current_page,
                                                      numpages=total_pages, archive_type=archive_type,
                                                      epoch=created))
            except Exception as ex:
                logger.error(f'Could not parse bookmarks file: \'{self.__bookmark_path}\'')
                logger.error(f'Exception: {ex}')

        return bookmarks

    def file_was_modified(self):
        """
        Checks the bookmark store's mtime to see if it has been modified
        since it was last read
        """

        if Path.is_file(self.__bookmark_path):
            if Path.stat(self.__bookmark_path).st_mtime > self.__bookmarks_mtime:
                return True
            return False

        return True

    def write_bookmarks_file(self):
        """
        Store relevant bookmark info in the mcomix directory
        """

        # Merge changes in case file was modified from within other instances
        if not self.__bookmark_state['dirty']:
            logger.info('No changes to write for bookmarks')
            return
        logger.info('Writing changes to bookmarks')

        if self.file_was_modified():
            new_bookmarks = self.load_bookmarks_file()
            self.__bookmarks = list(set(self.__bookmarks + new_bookmarks))

        packs = [bookmark.pack() for bookmark in self.__bookmarks]
        bookmarks = yaml.dump(packs, Dumper=yaml.CSafeDumper, sort_keys=False,
                              allow_unicode=True, width=2147483647)
        self.__bookmark_path.write_text(bookmarks)
        self.__bookmarks_mtime = time.time()

    def show_replace_bookmark_dialog(self, new_page):
        """
        Present a confirmation dialog to replace old bookmarks.

        :returns: RESPONSE_YES to create replace bookmarks,
        RESPONSE_NO to create a new bookmark, RESPONSE_CANCEL to abort creating
        a new bookmark
        """

        dialog = MessageDialog(
            self.__window,
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
