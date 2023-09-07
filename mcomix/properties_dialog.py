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

import stat
from datetime import datetime
from pathlib import Path

from gi.repository import Gtk

from mcomix.file_handler import FileHandler
from mcomix.file_size import format_filesize
from mcomix.image_handler import ImageHandler
from mcomix.lib.events import Events, EventType
from mcomix.properties_page import PropertiesPage

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class PropertiesDialog(Gtk.Dialog):
    def __init__(self, window: MainWindow):
        super().__init__(title='Properties')

        self.set_transient_for(window)
        self.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CANCEL)

        events = Events()
        events.add_event(EventType.FILE_OPENED, self._on_book_change)
        events.add_event(EventType.FILE_CLOSED, self._on_book_change)
        events.add_event(EventType.PAGE_AVAILABLE, self._on_page_available)
        events.add_event(EventType.PAGE_CHANGED, self._on_page_change)

        self.__file_handler = FileHandler(None)
        self.__image_handler = ImageHandler()

        self.resize(870, 560)
        self.set_border_width(2)
        self.set_resizable(True)
        self.set_default_response(Gtk.ResponseType.CLOSE)

        self.__notebook = Gtk.Notebook()
        self.vbox.pack_start(self.__notebook, True, True, 0)

        self.__notebook.set_border_width(2)

        self.__archive_page = PropertiesPage()
        self.__image_page = PropertiesPage()

        self.__notebook.append_page(self.__archive_page, Gtk.Label(label='Archive'))
        self.__notebook.append_page(self.__image_page, Gtk.Label(label='Image'))

        self._update_archive_page()
        self._update_image_page()

        self.show_all()

    def _on_page_change(self):
        self._update_image_page()

    def _on_book_change(self):
        self._update_archive_page()

    def _on_page_available(self, page_number: int):
        if page_number == 1:
            self._update_page_image(self.__archive_page, 1)
        current_page_number = self.__image_handler.get_current_page()
        if current_page_number == page_number:
            self._update_image_page()

    def _update_archive_page(self):
        page = self.__archive_page
        page.reset()
        if not self.__file_handler.is_archive():
            self.__notebook.detach_tab(page)
            return
        if self.__notebook.get_n_pages() == 1:
            self.__notebook.insert_page(page, Gtk.Label(label='Archive'), 0)
        self._update_page_image(page, 1)
        page.set_filename(self.__file_handler.get_real_path().name)
        path = self.__file_handler.get_base_path()
        main_info = (f'{self.__image_handler.get_number_of_pages()} pages',
                     'Archive File' if self.__file_handler.is_archive else 'Image File')
        page.set_main_info(main_info)
        self._update_page_secondary_info(page, path)
        page.show_all()

    def _update_image_page(self):
        page = self.__image_page
        page.reset()
        if not self.__image_handler.page_is_available():
            return
        self._update_page_image(page)
        path = self.__image_handler.get_path_to_page()
        page.set_filename(path.name)
        width, height = self.__image_handler.get_size()
        main_info = (f'{width}x{height} px', self.__image_handler.get_mime_name(),)
        page.set_main_info(main_info)
        self._update_page_secondary_info(page, path)
        page.show_all()

    def _update_page_image(self, page, page_number: int = None):
        if not self.__image_handler.page_is_available(page_number):
            return
        thumb = self.__image_handler.get_thumbnail(page=page_number, size=(256, 256))
        page.set_thumbnail(thumb)

    def _update_page_secondary_info(self, page, path: Path):
        stats = Path.stat(path)
        secondary_info = (
            ('Location', Path.resolve(path).parent),
            ('Size', format_filesize(path)),
            ('Modified', datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')),
            ('Accessed', datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S')),
            ('Permissions', oct(stat.S_IMODE(stats.st_mode))),
            ('Owner', path.owner()),
            ('Group', path.group())
        )
        page.set_secondary_info(secondary_info)
