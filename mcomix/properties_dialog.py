# -*- coding: utf-8 -*-

"""properties_dialog.py - Properties dialog that displays information about the archive/file"""

import stat
import time
from pathlib import Path

from gi.repository import Gtk

from mcomix.constants import Constants
from mcomix.image_handler import ImageHandler
from mcomix.preferences import prefs
from mcomix.properties_page import PropertiesPage


class PropertiesDialog(Gtk.Dialog):
    def __init__(self, window):
        super().__init__(title='Properties')

        self.set_transient_for(window)
        self.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.__window = window
        self.resize(prefs['PROPERTIES_WIDTH'], prefs['PROPERTIES_HEIGHT'])
        self.set_resizable(True)
        self.set_default_response(Gtk.ResponseType.CLOSE)

        self.__notebook = Gtk.Notebook()
        self.vbox.pack_start(self.__notebook, True, True, 0)
        self.set_border_width(4)
        self.__notebook.set_border_width(6)

        self.__archive_page = PropertiesPage()
        self.__image_page = PropertiesPage()

        self.__notebook.append_page(self.__archive_page, Gtk.Label(label='Archive'))
        self.__notebook.append_page(self.__image_page, Gtk.Label(label='Image'))

        self._update_archive_page()
        self.__window.page_changed += self._on_page_change
        self.__window.filehandler.file_opened += self._on_book_change
        self.__window.filehandler.file_closed += self._on_book_change
        self.__window.imagehandler.page_available += self._on_page_available

        self.show_all()

    def _on_page_change(self):
        self._update_image_page()

    def _on_book_change(self):
        self._update_archive_page()

    def _on_page_available(self, page_number: int):
        if page_number == 1:
            self._update_page_image(self.__archive_page, 1)
        current_page_number = self.__window.imagehandler.get_current_page()
        if current_page_number == page_number:
            self._update_image_page()

    def _update_archive_page(self):
        page = self.__archive_page
        page.reset()
        window = self.__window
        if window.filehandler.get_archive_type() is None:
            if self.__notebook.get_n_pages() == 2:
                self.__notebook.detach_tab(page)
            return
        if self.__notebook.get_n_pages() == 1:
            self.__notebook.insert_page(page, Gtk.Label(label='Archive'), 0)
        # In case it's not ready yet, bump the cover extraction
        # in front of the queue.
        path = window.imagehandler.get_path_to_page(1)
        if path is not None:
            window.filehandler.ask_for_files([path])
        self._update_page_image(page, 1)
        page.set_filename(window.filehandler.get_current_filename())
        path = window.filehandler.get_path_to_base()
        main_info = (
            f'{window.imagehandler.get_number_of_pages()} pages',
            Constants.ARCHIVE_DESCRIPTIONS[window.filehandler.get_archive_type()])
        page.set_main_info(main_info)
        self._update_page_secondary_info(page, path)
        page.show_all()
        self._update_image_page()

    def _update_image_page(self):
        page = self.__image_page
        page.reset()
        window = self.__window
        if not window.imagehandler.page_is_available():
            return
        self._update_page_image(page)
        path = Path() / window.imagehandler.get_path_to_page()
        page.set_filename(path.name)
        width, height = window.imagehandler.get_size()
        main_info = (f'{width}x{height} px', window.imagehandler.get_mime_name(),)
        page.set_main_info(main_info)
        self._update_page_secondary_info(page, path)
        page.show_all()

    def _update_page_image(self, page, page_number: int = None):
        if not self.__window.imagehandler.page_is_available(page_number):
            return
        size = prefs['PROPERTIES_THUMB_SIZE']
        thumb = self.__window.imagehandler.get_thumbnail(page_number, size=(size, size))
        page.set_thumbnail(thumb)

    @staticmethod
    def _update_page_secondary_info(page, path: Path):
        path = Path() / path
        stats = Path.stat(path)
        uid = Path.owner(path)
        gid = Path.group(path)
        secondary_info = [
            ('Location', Path.resolve(path).parent),
            ('Size', ImageHandler.format_byte_size(stats.st_size)),
            ('Modified', time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime(stats.st_mtime))),
            ('Accessed', time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime(stats.st_atime))),
            ('Permissions', oct(stat.S_IMODE(stats.st_mode))),
            ('Owner', uid),
            ('Group', gid)
        ]
        page.set_secondary_info(secondary_info)
