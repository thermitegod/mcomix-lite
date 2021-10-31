# -*- coding: utf-8 -*-

"""status.py - Statusbar for main window"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from gi.repository import Gtk

from mcomix.file_size import FileSize
from mcomix.enums.image_scaling import ScalingGDK, ScalingPIL
from mcomix.preferences import config


class Statusbar(Gtk.EventBox):
    def __init__(self):
        super().__init__()

        # statusbar field separator
        self.__sep = '  |  '

        # Status text layout
        # page number, file number, page resolution, archive filename,
        # page filename, page filesize, archive filesize, view mode
        self.__status = Gtk.Statusbar()

        # margin padding, gtk3 defaults are too large
        self.__status.set_margin_top(2)
        self.__status.set_margin_bottom(2)

        self.add(self.__status)

        self.__context_id = self.__status.get_context_id('statusbar')

        self.__context_menu = Gtk.Menu()

        @dataclass(frozen=True)
        class STATUSBAR:
            __slots__ = ['label', 'config_key', 'callback']
            label: str
            config_key: str
            callback: Callable

        context_menu_items = (
            STATUSBAR('Show page numbers',
                      'STATUSBAR_FIELD_PAGE_NUMBERS',
                      self._toggle_status_visibility),
            STATUSBAR('Show file numbers',
                      'STATUSBAR_FIELD_FILE_NUMBERS',
                      self._toggle_status_visibility),
            STATUSBAR('Show page resolution',
                      'STATUSBAR_FIELD_PAGE_RESOLUTION',
                      self._toggle_status_visibility),
            STATUSBAR('Show archive filename',
                      'STATUSBAR_FIELD_ARCHIVE_NAME',
                      self._toggle_status_visibility),
            STATUSBAR('Show page filename',
                      'STATUSBAR_FIELD_PAGE_FILENAME',
                      self._toggle_status_visibility),
            STATUSBAR('Show page filesize',
                      'STATUSBAR_FIELD_PAGE_FILESIZE',
                      self._toggle_status_visibility),
            STATUSBAR('Show archive filesize',
                      'STATUSBAR_FIELD_ARCHIVE_FILESIZE',
                      self._toggle_status_visibility),
            STATUSBAR('Show page scaling',
                      'STATUSBAR_FIELD_PAGE_SCALING',
                      self._toggle_status_visibility),
            STATUSBAR('Show current mode',
                      'STATUSBAR_FIELD_VIEW_MODE',
                      self._toggle_status_visibility),
        )

        for item in context_menu_items:
            self._populate_context_menu(label=item.label, config_key=item.config_key, callback=item.callback)

        # Hook mouse release event
        self.connect('button-press-event', self._button_released)

        # Default status information
        self.__total_page_numbers = ''
        self.__total_file_numbers = ''
        self.__page_resolution = ''
        self.__archive_filename = ''
        self.__page_filename = ''
        self.__page_filesize = ''
        self.__archive_filesize = ''
        self.__image_scaling = ''
        self.__current_view_mode = ''

        self.show_all()

        self.update_image_scaling()

    def update_image_scaling(self):
        # is initalized here and only updated if the
        # scaling algos get changed

        if config['ENABLE_PIL_SCALING']:
            self.__image_scaling = f'PIL: {ScalingPIL(config["PIL_SCALING_FILTER"]).name}'
        else:
            self.__image_scaling = f'GDK: {ScalingGDK(config["GDK_SCALING_FILTER"]).name}'

    def set_message(self, message: str):
        """
        Set a specific message (such as an error message) on the statusbar,
        replacing whatever was there earlier
        """

        self.__status.pop(self.__context_id)
        self.__status.push(self.__context_id, f'    {message}')

    def set_page_number(self, page: int, total_pages: int, displayed_double: bool, manga_mode: bool):
        """
        Update the page number
        """

        if displayed_double:
            if manga_mode:
                p = f'{page + 1}, {page}'
            else:
                p = f'{page}, {page + 1}'
        else:
            p = f'{page}'

        self.__total_page_numbers = f'{p} / {total_pages}'

    def set_view_mode(self, is_manga_mode: bool):
        """
        Update the mode
        """

        if is_manga_mode:
            self.__current_view_mode = 'Manga'
        else:
            self.__current_view_mode = 'Western'

    def set_file_number(self, fileno: int, total: int):
        """
        Updates the file number (i.e. number of current file/total files loaded)
        """

        self.__total_file_numbers = f'{fileno} / {total}'

    def set_resolution(self, dimensions: list):  # 2D only
        """
        Update the resolution data.
        Takes an iterable of tuples, (x, y, scale), describing the original
        resolution of an image as well as the currently displayed scale
        """

        if config['STATUSBAR_SHOW_SCALE']:
            self.__page_resolution = ', '.join(f'{d[0]}x{d[1]} ({d[2]:.2%})' for d in dimensions)
        else:
            self.__page_resolution = ', '.join(f'{d[0]}x{d[1]}' for d in dimensions)

    def set_archive_filename(self, root: Path):
        """
        Set the name of the root (directory or archive)
        """

        self.__archive_filename = str(root)

    def set_filename(self, filename: str):
        """
        Update the filename
        """

        self.__page_filename = filename

    def set_filesize(self, size: str):
        """
        Update the filesize
        """

        if size is None:
            size = ''
        self.__page_filesize = size

    def set_filesize_archive(self, path: Path):
        """
        Update the filesize
        """

        self.__archive_filesize = FileSize(path)

    def update(self):
        """
        Set the statusbar to display the current state
        """

        text = ''

        if config['STATUSBAR_FIELD_PAGE_NUMBERS']:
            text += f'{self.__total_page_numbers}{self.__sep}'
        if config['STATUSBAR_FIELD_FILE_NUMBERS']:
            text += f'{self.__total_file_numbers}{self.__sep}'
        if config['STATUSBAR_FIELD_PAGE_RESOLUTION']:
            text += f'{self.__page_resolution}{self.__sep}'
        if config['STATUSBAR_FIELD_ARCHIVE_NAME']:
            text += f'{self.__archive_filename}{self.__sep}'
        if config['STATUSBAR_FIELD_PAGE_FILENAME']:
            text += f'{self.__page_filename}{self.__sep}'
        if config['STATUSBAR_FIELD_PAGE_FILESIZE']:
            text += f'{self.__page_filesize}{self.__sep}'
        if config['STATUSBAR_FIELD_ARCHIVE_FILESIZE']:
            text += f'{self.__archive_filesize}{self.__sep}'
        if config['STATUSBAR_FIELD_PAGE_SCALING']:
            text += f'{self.__image_scaling}{self.__sep}'
        if config['STATUSBAR_FIELD_VIEW_MODE']:
            text += f'{self.__current_view_mode}{self.__sep}'

        self.set_message(message=text.strip(self.__sep))

    def _populate_context_menu(self, label: str, config_key: str, callback: Callable):
        item = Gtk.CheckMenuItem(label=label)
        item.set_active(config[config_key])
        item.connect('activate', callback, config_key)
        item.show_all()
        self.__context_menu.append(item)

    def _toggle_status_visibility(self, widget, config_statusbar):
        """
        Called when status entries visibility is to be changed
        """

        config[config_statusbar] = not config[config_statusbar]

        self.update()

    def _button_released(self, widget, event, *args):
        if event.button == 3:
            self.__context_menu.popup(None, None, None, None, event.button, event.time)
