# -*- coding: utf-8 -*-

"""bookmark_backend.py - Bookmarks handler"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml
from gi.repository import Gtk
from loguru import logger

from mcomix.bookmark_menu_item import Bookmark
from mcomix.enums.config_files import ConfigFiles
from mcomix.file_handler import FileHandler
from mcomix.image_handler import ImageHandler
from mcomix.lib.events import Events, EventType
from mcomix.message_dialog.info import MessageDialogInfo
from mcomix.message_dialog.remember import MessageDialogRemember

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class BookmarkBackend:
    """
    The _BookmarkBackend is a backend for both the bookmarks menu and dialog.
    Changes in the _BookmarkBackend are mirrored in both
    """

    def __init__(self, window: MainWindow):
        super().__init__()

        self.__window = window

        self.__events = Events()

        self.__file_handler = FileHandler(None)
        self.__image_handler = ImageHandler()

        self.__bookmark_path = ConfigFiles.BOOKMARK.value
        self.__bookmark_state_dirty = False

        #: List of bookmarks
        self.__bookmarks = self.load_bookmarks_file()
        #: Modification date of bookmarks file
        self.__bookmarks_size = self.get_bookmarks_file_size()

    def add_bookmark(self, bookmark):
        """
        Add the <bookmark> to the list
        """

        self.__bookmarks.append(bookmark)
        self.write_bookmarks_file()

        self.__events.run_events(EventType.BOOKMARK_ADD)

    def remove_bookmark(self, bookmark):
        """
        Remove the <bookmark> from the list
        """

        self.__bookmarks.remove(bookmark)
        self.write_bookmarks_file()

        self.__events.run_events(EventType.BOOKMARK_REMOVE)

    def add_current_to_bookmarks(self):
        """
        Add the currently viewed page to the list
        """

        path = self.__file_handler.get_real_path()
        current_page = self.__image_handler.get_current_page()
        total_pages = self.__image_handler.get_number_of_pages()
        date_added = datetime.today().timestamp()

        same_file_bookmarks = []

        for bookmark in self.__bookmarks:
            if Path(bookmark.bookmark_path) == path:
                if bookmark.bookmark_current_page == current_page:
                    logger.info(f'Bookmark already exists for file \'{path}\' on page \'{current_page}\'')
                    return

                same_file_bookmarks.append(bookmark)

        # If the same file was already bookmarked, ask to replace
        # the existing bookmarks before deleting them.
        if len(same_file_bookmarks) > 0:
            response = self.show_replace_bookmark_dialog(current_page)

            # Delete old bookmarks
            if response == Gtk.ResponseType.YES:
                for bookmark in same_file_bookmarks:
                    self.remove_bookmark(bookmark)
            # Perform no action
            elif response not in (Gtk.ResponseType.YES, Gtk.ResponseType.NO):
                return

        bookmark = Bookmark(self.__window, path, current_page, total_pages, date_added)
        self.add_bookmark(bookmark)

    def open_bookmark(self, path: Path, current_page: int):
        """
        Open the file and page the bookmark represents
        """

        if not path.is_file():
            dialog = MessageDialogInfo()
            dialog.set_text(primary='Bookmarked file does not exist', secondary=f'{path}')
            dialog.run()
            return

        if self.__file_handler.get_real_path() != path:
            self.__file_handler.open_file_init(paths=[path], start_page=current_page)
        else:
            self.__window.set_page(current_page)

    def get_bookmarks(self):
        """
        Return all the bookmarks in the list
        """

        if not self.file_was_modified():
            return self.__bookmarks

        self.__bookmarks = self.load_bookmarks_file()
        return self.__bookmarks

    def get_bookmarks_file_size(self):
        if not self.__bookmark_path.is_file():
            return 0

        return self.__bookmark_path.stat().st_size

    def load_bookmarks_file(self):
        """
        Loads persisted bookmarks from a local file.

        :return: Tuple of (bookmarks, file mtime)
        """

        bookmarks = []

        if not Path.is_file(self.__bookmark_path):
            return bookmarks

        try:
            with Path.open(self.__bookmark_path, mode='rt', encoding='utf8') as fd:
                for bookmark in yaml.safe_load(fd):
                    for item in bookmark:
                        path = Path(bookmark[item]['path'], item)
                        current_page = bookmark[item]['current_page']
                        total_pages = bookmark[item]['total_pages']
                        date_added = bookmark[item]['created']

                        # if not path.is_file():
                        #     logger.warning(f'Missing bookmark: {path}')

                        bookmarks.append(Bookmark(self.__window, path=path, current_page=current_page,
                                                  total_pages=total_pages, date_added=date_added))
        except Exception as ex:
            logger.error(f'Could not parse bookmarks file: \'{self.__bookmark_path}\'')
            logger.error(f'Exception: {ex}')

        return bookmarks

    def bookmark_pack(self, bookmark):
        """
        Returns a dict. The bookmark can be fully
        re-created using the values in the dict
        """

        return {
            bookmark.bookmark_name: {
                # YAML does not work with Pathlike objects
                # when using CSafeDumper
                'path': str(Path(bookmark.bookmark_path).parent),
                'current_page': bookmark.bookmark_current_page,
                'total_pages': bookmark.bookmark_total_pages,
                # archive_type is deprecated, to be removed before next release
                'archive_type': 0,
                'created': bookmark.bookmark_date_added
            }
        }

    def file_was_modified(self):
        """
        Checks the bookmark store's mtime to see if it has been modified
        since it was last read
        """

        if not self.__bookmark_path.is_file() or \
                (self.get_bookmarks_file_size() != self.__bookmarks_size):
            return True

        return False

    def write_bookmarks_file(self, force_write: bool = False):
        """
        Store relevant bookmark info in the mcomix directory
        """

        # Merge changes in case file was modified from within other instances
        if not self.__bookmark_state_dirty or force_write:
            logger.info('No changes to write for bookmarks')
            return
        logger.info('Writing changes to bookmarks')

        if self.file_was_modified():
            new_bookmarks = self.load_bookmarks_file()
            self.__bookmarks = list(set(self.__bookmarks + new_bookmarks))

        packs = [self.bookmark_pack(bookmark) for bookmark in self.__bookmarks]
        bookmarks = yaml.dump(packs, Dumper=yaml.CSafeDumper, sort_keys=False,
                              allow_unicode=True, width=2147483647)
        self.__bookmark_path.write_text(bookmarks)
        self.__bookmarks_size = self.get_bookmarks_file_size()

    def show_replace_bookmark_dialog(self, new_page):
        """
        Present a confirmation dialog to replace old bookmarks.

        :returns: RESPONSE_YES to create replace bookmarks,
        RESPONSE_NO to create a new bookmark, RESPONSE_CANCEL to abort creating
        a new bookmark
        """

        dialog = MessageDialogRemember()
        dialog.add_buttons(
            Gtk.STOCK_YES, Gtk.ResponseType.YES,
            Gtk.STOCK_NO, Gtk.ResponseType.NO,
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.set_default_response(Gtk.ResponseType.YES)
        dialog.set_should_remember_choice('replace-existing-bookmark', (Gtk.ResponseType.YES, Gtk.ResponseType.NO))
        dialog.set_text(primary='The current book already contains marked pages.',
                        secondary=f'Do you want to replace them with a new bookmark on page {new_page}?'
                                  'Selecting "No" will create a new bookmark.')

        return dialog.run()
