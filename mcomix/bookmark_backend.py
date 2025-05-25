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

import tomli, tomli_w

from gi.repository import Gtk
from loguru import logger

from platformdirs import *

from mcomix.gui.bookmark_menu_item import Bookmark
from mcomix.lib.events import Events, EventType
from mcomix.gui.dialog.info import MessageDialogInfo
from mcomix.gui.dialog.remember import MessageDialogRemember

from mcomix_compiled import PackageInfo

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.gui.main_window import MainWindow


class BookmarkBackend:
    """
    The _BookmarkBackend is a backend for both the bookmarks menu and dialog.
    Changes in the _BookmarkBackend are mirrored in both
    """

    def __init__(self, window: MainWindow):
        super().__init__()

        self.__window = window

        self.__events = Events()

        self.__bookmark_path: Path = Path(user_config_dir(PackageInfo.PROG_NAME)) / 'bookmarks.toml'
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
        self.write_bookmarks_file(force_write=True)

        self.__events.run_events(EventType.BOOKMARK_ADD)

    def remove_bookmark(self, bookmark):
        """
        Remove the <bookmark> from the list
        """

        self.__bookmarks.remove(bookmark)
        self.write_bookmarks_file(force_write=True)

        self.__events.run_events(EventType.BOOKMARK_REMOVE)

    def add_current_to_bookmarks(self):
        """
        Add the currently viewed page to the list
        """

        path = self.__window.file_handler.get_real_path()
        current_page = self.__window.image_handler.get_current_page()
        total_pages = self.__window.image_handler.get_number_of_pages()
        date_added = datetime.today().timestamp()

        same_file_bookmarks = []

        for bookmark in self.__bookmarks:
            if Path(bookmark.bookmark_path) == path:
                if bookmark.bookmark_current_page == current_page:
                    message = f'Bookmark already exists for file \'{path}\' on page \'{current_page}\''
                    logger.info(message)

                    dialog = MessageDialogInfo()
                    dialog.set_text(primary='Already Bookmarked', secondary=message)
                    dialog.run()

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

        path = Path(path)

        if not path.is_file():
            dialog = MessageDialogInfo()
            dialog.set_text(primary='Bookmarked file does not exist', secondary=f'{path}')
            dialog.run()
            return

        if self.__window.file_handler.get_real_path() != path:
            self.__window.file_handler.open_file_init(paths=[path], start_page=current_page)
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
        bookmarks_raw = dict()

        if not self.__bookmark_path.is_file():
            return bookmarks
        try:
            contents: str
            with self.__bookmark_path.open(mode='rt') as fd:
                # not using 'contents' will throw
                # Exception: '_io.TextIOWrapper' object has no attribute 'replace'
                contents = fd.read()
            bookmarks_raw = tomli.loads(contents)['Bookmarks']
        except tomli.TOMLDecodeError as e:
            logger.error(f'Could not parse TOML bookmarks file: \'{self.__bookmark_path}\'')
            logger.debug(f'Exception: {e}')
            self.__bookmark_path.rename(f'{self.__bookmark_path}.bak-{int(datetime.timestamp(datetime.now()))}')
            return bookmarks
        except Exception as e:
            logger.error(f'Could load bookmarks file: \'{self.__bookmark_path}\'')
            logger.debug(f'Exception: {e}')
            self.__bookmark_path.rename(f'{self.__bookmark_path}.bak-{int(datetime.timestamp(datetime.now()))}')
            return bookmarks

        for bookmark in bookmarks_raw:
            for item in bookmark:
                path = Path(bookmark[item]['path'], item)
                current_page = bookmark[item]['current_page']
                total_pages = bookmark[item]['total_pages']
                date_added = bookmark[item]['created']

                # if not path.is_file():
                #     logger.warning(f'Missing bookmark: {path}')

                bookmarks.append(Bookmark(self.__window, path=path, current_page=current_page,
                                          total_pages=total_pages, date_added=date_added))

        return bookmarks

    def bookmark_pack(self, bookmark):
        """
        Returns a dict. The bookmark can be fully
        re-created using the values in the dict
        """

        return {
            bookmark.bookmark_name: {
                'path': str(Path(bookmark.bookmark_path).parent),
                'current_page': bookmark.bookmark_current_page,
                'total_pages': bookmark.bookmark_total_pages,
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

    def write_bookmarks_file(self, *, force_write: bool = False):
        """
        Store relevant bookmark info in the mcomix directory
        """

        if force_write:
            self.__bookmark_state_dirty = True

        # Merge changes in case file was modified from within other instances
        if not self.__bookmark_state_dirty:
            logger.info('No changes to write for bookmarks')
            return
        logger.info('Writing changes to bookmarks')

        if self.file_was_modified():
            new_bookmarks = self.load_bookmarks_file()
            self.__bookmarks = list(set(self.__bookmarks + new_bookmarks))

        packs = [self.bookmark_pack(bookmark) for bookmark in self.__bookmarks]
        bookmarks = tomli_w.dumps({'Bookmarks': packs})
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
        dialog.add_buttons(Gtk.STOCK_YES, Gtk.ResponseType.YES)
        dialog.add_buttons(Gtk.STOCK_NO, Gtk.ResponseType.NO)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.set_default_response(Gtk.ResponseType.YES)
        dialog.set_should_remember_choice('replace-existing-bookmark', (Gtk.ResponseType.YES, Gtk.ResponseType.NO))
        dialog.set_text(primary='The current book already contains marked pages.',
                        secondary=f'Do you want to replace them with a new bookmark on page {new_page}?'
                                  'Selecting "No" will create a new bookmark.')

        return dialog.run()
