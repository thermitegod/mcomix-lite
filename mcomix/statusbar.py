# -*- coding: utf-8 -*-

"""status.py - Statusbar for main window"""

from collections import namedtuple
from pathlib import Path
from typing import Callable

from gi.repository import Gdk, Gtk

from mcomix.file_size import FileSize
from mcomix.preferences import config


class Statusbar(Gtk.EventBox):
    def __init__(self):
        super().__init__()

        self.__spacing = 5

        self.__loading = True

        # Status text layout
        # page number, file number, page resolution, archive filename,
        # page filename, page filesize, archive filesize, view mode
        self.__status = Gtk.Statusbar()
        self.add(self.__status)

        self.__context_menu = Gtk.Menu()

        STATUSBAR = namedtuple('STATUSBAR', ['label', 'config_key', 'callback'])
        self.__context_menu_items = (
            STATUSBAR('Show page numbers',
                      'STATUSBAR_FIELD_PAGE_NUMBERS',
                      self._toggle_status_page_numbers),
            STATUSBAR('Show file numbers',
                      'STATUSBAR_FIELD_FILE_NUMBERS',
                      self._toggle_status_file_numbers),
            STATUSBAR('Show page resolution',
                      'STATUSBAR_FIELD_PAGE_RESOLUTION',
                      self._toggle_status_page_resolution),
            STATUSBAR('Show archive filename',
                      'STATUSBAR_FIELD_ARCHIVE_NAME',
                      self._toggle_status_archive_name),
            STATUSBAR('Show page filename',
                      'STATUSBAR_FIELD_PAGE_FILENAME',
                      self._toggle_status_page_filename),
            STATUSBAR('Show page filesize',
                      'STATUSBAR_FIELD_PAGE_FILESIZE',
                      self._toggle_status_page_filesize),
            STATUSBAR('Show archive filesize',
                      'STATUSBAR_FIELD_ARCHIVE_FILESIZE',
                      self._toggle_status_archive_filesize),
            STATUSBAR('Show page scaling',
                      'STATUSBAR_FIELD_PAGE_SCALING',
                      self._toggle_status_page_scale),
            STATUSBAR('Show current mode',
                      'STATUSBAR_FIELD_VIEW_MODE',
                      self._toggle_status_view_mode),
        )

        for item in self.__context_menu_items:
            self._populate_context_menu(label=item.label, config_key=item.config_key, callback=item.callback)

        # Hook mouse release event
        self.connect('button-release-event', self._button_released)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)

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

        self.__loading = False

        self.update_image_scaling()

    def update_image_scaling(self):
        # is initalized here and only updated if the
        # scaling algos get changed

        scale_main = (
            'Nearest',
            'Tiles',
            'Bilinear'
        )[config['SCALING_QUALITY']]

        scale_sub = (
            'None',
            'Nearest',
            'Lanczos',
            'Bilinear',
            'Bicubic',
            'Box',
            'Hamming',
        )[config['PIL_SCALING_FILTER'] + 1]

        self.__image_scaling = f'{scale_main}, {scale_sub}'

    def set_message(self, message: str):
        """
        Set a specific message (such as an error message) on the statusbar,
        replacing whatever was there earlier
        """

        self.__status.pop(0)
        self.__status.push(0, f'    {message}')

    def set_page_number(self, page: int, total: int, this_screen: int):
        """
        Update the page number
        """

        p = ', '.join(str(page + i) for i in range(this_screen))
        self.__total_page_numbers = f'{p} / {total}'

    def get_page_number(self):
        """
        :returns: the bar's page information
        """

        return self.__total_page_numbers

    def get_mode(self):
        return self.__current_view_mode

    def set_mode(self):
        """
        Update the mode
        """

        if config['DEFAULT_MANGA_MODE']:
            self.__current_view_mode = 'Manga'
        else:
            self.__current_view_mode = 'Western'

    def set_file_number(self, fileno: int, total: int):
        """
        Updates the file number (i.e. number of current file/total files loaded)
        """

        if total > 0:
            self.__total_file_numbers = f'{fileno} / {total}'
        else:
            self.__total_file_numbers = ''

    def get_file_number(self):
        """
        Returns the bar's file information
        """

        return self.__total_file_numbers

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

    def set_root(self, root: str):
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

        self.__archive_filesize = FileSize(path).size

    def update(self):
        """
        Set the statusbar to display the current state
        """

        sep = config['STATUSBAR_SEPARATOR']
        s = f'{sep:^{self.__spacing}}'
        text = ''

        if config['STATUSBAR_FIELD_PAGE_NUMBERS']:
            text += f'{self.__total_page_numbers}{s}'
        if config['STATUSBAR_FIELD_FILE_NUMBERS']:
            text += f'{self.__total_file_numbers}{s}'
        if config['STATUSBAR_FIELD_PAGE_RESOLUTION']:
            text += f'{self.__page_resolution}{s}'
        if config['STATUSBAR_FIELD_ARCHIVE_NAME']:
            text += f'{self.__archive_filename}{s}'
        if config['STATUSBAR_FIELD_PAGE_FILENAME']:
            text += f'{self.__page_filename}{s}'
        if config['STATUSBAR_FIELD_PAGE_FILESIZE']:
            text += f'{self.__page_filesize}{s}'
        if config['STATUSBAR_FIELD_ARCHIVE_FILESIZE']:
            text += f'{self.__archive_filesize}{s}'
        if config['STATUSBAR_FIELD_PAGE_SCALING']:
            text += f'{self.__image_scaling}{s}'
        if config['STATUSBAR_FIELD_VIEW_MODE']:
            text += f'{self.__current_view_mode}{s}'

        self.__status.pop(0)
        self.__status.push(0, f'    {text}')

    def _populate_context_menu(self, label: str, config_key: str, callback: Callable):
        item = Gtk.CheckMenuItem(label)
        item.set_active(config[config_key])
        item.connect('activate', callback)
        item.show_all()
        self.__context_menu.append(item)

    def _toggle_status_page_numbers(self, *args):
        self._toggle_status_visibility('STATUSBAR_FIELD_PAGE_NUMBERS')

    def _toggle_status_file_numbers(self, *args):
        self._toggle_status_visibility('STATUSBAR_FIELD_FILE_NUMBERS')

    def _toggle_status_page_resolution(self, *args):
        self._toggle_status_visibility('STATUSBAR_FIELD_PAGE_RESOLUTION')

    def _toggle_status_archive_name(self, *args):
        self._toggle_status_visibility('STATUSBAR_FIELD_ARCHIVE_NAME')

    def _toggle_status_page_filename(self, *args):
        self._toggle_status_visibility('STATUSBAR_FIELD_PAGE_FILENAME')

    def _toggle_status_page_filesize(self, *args):
        self._toggle_status_visibility('STATUSBAR_FIELD_PAGE_FILESIZE')

    def _toggle_status_archive_filesize(self, *args):
        self._toggle_status_visibility('STATUSBAR_FIELD_ARCHIVE_FILESIZE')

    def _toggle_status_page_scale(self, *args):
        self._toggle_status_visibility('STATUSBAR_FIELD_PAGE_SCALING')

    def _toggle_status_view_mode(self, *args):
        self._toggle_status_visibility('STATUSBAR_FIELD_VIEW_MODE')

    def _toggle_status_visibility(self, config_statusbar):
        """
        Called when status entries visibility is to be changed
        """

        # Ignore events as long as control is still loading.
        if self.__loading:
            return

        config[config_statusbar] = not config[config_statusbar]

        self.update()

    def _button_released(self, widget, event, *args):
        if event.button == 3:
            self.__context_menu.popup(None, None, None, None, event.button, event.time)
