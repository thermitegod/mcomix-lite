# -*- coding: utf-8 -*-

"""status.py - Statusbar for main window"""

from pathlib import Path

from gi.repository import Gdk, Gtk

from mcomix.constants import Constants
from mcomix.preferences import config
from mcomix.utils import Utils


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

        # Create popup menu for enabling/disabling status boxes.
        self.__ui_manager = Gtk.UIManager()
        ui_description = """
        <ui>
            <popup name="Statusbar">
                <menuitem action="total_page_numbers"/>
                <menuitem action="total_file_numbers"/>
                <menuitem action="page_resolution"/>
                <menuitem action="archive_filename"/>
                <menuitem action="page_filename"/>
                <menuitem action="page_filesize"/>
                <menuitem action="archive_filesize"/>
                <menuitem action="current_view_mode"/>
            </popup>
        </ui>
        """
        self.__ui_manager.add_ui_from_string(ui_description)

        actiongroup = Gtk.ActionGroup(name='mcomix-statusbar')
        actiongroup.add_toggle_actions([
            ('total_page_numbers', None, 'Show page numbers', None, None, self.toggle_status_visibility),
            ('total_file_numbers', None, 'Show file numbers', None, None, self.toggle_status_visibility),
            ('page_resolution', None, 'Show page resolution', None, None, self.toggle_status_visibility),
            ('archive_filename', None, 'Show archive name', None, None, self.toggle_status_visibility),
            ('page_filename', None, 'Show page filename', None, None, self.toggle_status_visibility),
            ('page_filesize', None, 'Show page filesize', None, None, self.toggle_status_visibility),
            ('archive_filesize', None, 'Show archive filesize', None, None, self.toggle_status_visibility),
            ('current_view_mode', None, 'Show current mode', None, None, self.toggle_status_visibility)])
        self.__ui_manager.insert_action_group(actiongroup, 0)

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
        self.__current_view_mode = ''
        self._update_sensitivity()
        self.show_all()

        self.__loading = False

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
            self.__total_file_numbers = f'({fileno} / {total})'
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

        self.__page_resolution = ', '.join(f'{d[0]}x{d[1]} ({d[2]:.2%})' for d in dimensions)

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

        self.__archive_filesize = Utils.format_byte_size(Path.stat(path).st_size)

    def update(self):
        """
        Set the statusbar to display the current state
        """

        sep = config['STATUSBAR_SEPARATOR']

        s = f'{sep:^{self.__spacing}}'
        text = s.join(self._get_status_text())
        self.__status.pop(0)
        self.__status.push(0, f'    {text}')

    def _get_status_text(self):
        """
        Returns an array of text fields that should be displayed
        """

        fields = [
            (Constants.STATUSBAR['PAGE_NUMBERS'], self.__total_page_numbers),
            (Constants.STATUSBAR['FILE_NUMBERS'], self.__total_file_numbers),
            (Constants.STATUSBAR['PAGE_RESOLUTION'], self.__page_resolution),
            (Constants.STATUSBAR['ARCHIVE_NAME'], self.__archive_filename),
            (Constants.STATUSBAR['PAGE_FILENAME'], self.__page_filename),
            (Constants.STATUSBAR['PAGE_FILESIZE'], self.__page_filesize),
            (Constants.STATUSBAR['ARCHIVE_FILESIZE'], self.__archive_filesize),
            (Constants.STATUSBAR['VIEW_MODE'], self.__current_view_mode),
        ]
        p = config['STATUSBAR_FIELDS']

        return [s for c, s in filter(lambda f: f[0] & p, fields)]

    def toggle_status_visibility(self, action, *args):
        """
        Called when status entries visibility is to be changed
        """

        # Ignore events as long as control is still loading.
        if self.__loading:
            return

        names = {
            'total_page_numbers': Constants.STATUSBAR['PAGE_NUMBERS'],
            'total_file_numbers': Constants.STATUSBAR['FILE_NUMBERS'],
            'page_resolution': Constants.STATUSBAR['PAGE_RESOLUTION'],
            'archive_filename': Constants.STATUSBAR['ARCHIVE_NAME'],
            'page_filename': Constants.STATUSBAR['PAGE_FILENAME'],
            'page_filesize': Constants.STATUSBAR['PAGE_FILESIZE'],
            'archive_filesize': Constants.STATUSBAR['ARCHIVE_FILESIZE'],
            'current_view_mode': Constants.STATUSBAR['VIEW_MODE'],
        }

        bit = names[action.get_name()]

        if action.get_active():
            config['STATUSBAR_FIELDS'] |= bit
        else:
            config['STATUSBAR_FIELDS'] &= ~bit

        self.update()
        self._update_sensitivity()

    def _button_released(self, widget, event, *args):
        """
        Triggered when a mouse button is released to open the context menu
        """

        if event.button == 3:
            self.__ui_manager.get_widget('/Statusbar').popup(None, None, None, None, event.button, event.time)

    def _update_sensitivity(self):
        """
        Updates the action menu's sensitivity based on user preferences
        """

        p = config['STATUSBAR_FIELDS']
        names = {
            'total_page_numbers': p & Constants.STATUSBAR['PAGE_NUMBERS'],
            'total_file_numbers': p & Constants.STATUSBAR['FILE_NUMBERS'],
            'page_resolution': p & Constants.STATUSBAR['PAGE_RESOLUTION'],
            'archive_filename': p & Constants.STATUSBAR['ARCHIVE_NAME'],
            'page_filename': p & Constants.STATUSBAR['PAGE_FILENAME'],
            'page_filesize': p & Constants.STATUSBAR['PAGE_FILESIZE'],
            'archive_filesize': p & Constants.STATUSBAR['ARCHIVE_FILESIZE'],
            'current_view_mode': p & Constants.STATUSBAR['VIEW_MODE'],
        }

        for n, v in names.items():
            action = self.__ui_manager.get_action(f'/Statusbar/{n}')
            action.set_active(v)
