# -*- coding: utf-8 -*-

"""properties_dialog.py - Properties dialog that displays information about the archive/file"""

import stat
from datetime import datetime
from pathlib import Path

from gi.repository import Gtk

from mcomix.file_size import FileSize
from mcomix.preferences import config
from mcomix.properties_page import PropertiesPage


class PropertiesDialog(Gtk.Dialog):
    __slots__ = ('__window', '__notebook', '__archive_page', '__image_page')

    def __init__(self, window):
        super().__init__(title='Properties')

        self.set_transient_for(window)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)

        self.__window = window
        self.resize(config['PROPERTIES_WIDTH'], config['PROPERTIES_HEIGHT'])
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
        if not window.filehandler.is_archive():
            if self.__notebook.get_n_pages() == 2:
                self.__notebook.detach_tab(page)
            return
        if self.__notebook.get_n_pages() == 1:
            self.__notebook.insert_page(page, Gtk.Label(label='Archive'), 0)
        self._update_page_image(page, 1)
        page.set_filename(window.filehandler.get_current_filename())
        path = window.filehandler.get_path_to_base()
        main_info = (f'{window.imagehandler.get_number_of_pages()} pages',
                     'Archive File' if window.filehandler.is_archive else 'Image File')
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
        path = window.imagehandler.get_path_to_page()
        page.set_filename(path.name)
        width, height = window.imagehandler.get_size()
        main_info = (f'{width}x{height} px', window.imagehandler.get_mime_name(),)
        page.set_main_info(main_info)
        self._update_page_secondary_info(page, path)
        page.show_all()

    def _update_page_image(self, page, page_number: int = None):
        if not self.__window.imagehandler.page_is_available(page_number):
            return
        size = config['PROPERTIES_THUMB_SIZE']
        thumb = self.__window.imagehandler.get_thumbnail(page=page_number, size=(size, size))
        page.set_thumbnail(thumb)

    def _update_page_secondary_info(self, page, path: Path):
        stats = Path.stat(path)
        secondary_info = (
            ('Location', Path.resolve(path).parent),
            ('Size', FileSize(path)),
            ('Modified', datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')),
            ('Accessed', datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S')),
            ('Permissions', oct(stat.S_IMODE(stats.st_mode))),
            ('Owner', path.owner()),
            ('Group', path.group())
        )
        page.set_secondary_info(secondary_info)
