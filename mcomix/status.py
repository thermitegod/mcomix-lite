# -*- coding: utf-8 -*-

"""status.py - Statusbar for main window"""

from gi.repository import Gdk, Gtk

from mcomix import constants
from mcomix.preferences import prefs


class Statusbar(Gtk.EventBox):
    def __init__(self):
        super().__init__()

        self.__spacing = prefs['statusbar spacing']

        self.__loading = True

        # Status text, page number, file number, resolution, path, filename, filesize
        self.__status = Gtk.Statusbar()
        self.add(self.__status)

        # Create popup menu for enabling/disabling status boxes.
        self.__ui_manager = Gtk.UIManager()
        ui_description = """
        <ui>
            <popup name="Statusbar">
                <menuitem action="pagenumber"/>
                <menuitem action="filenumber"/>
                <menuitem action="resolution"/>
                <menuitem action="rootpath"/>
                <menuitem action="filename"/>
                <menuitem action="filesize"/>
                <menuitem action="view mode"/>
            </popup>
        </ui>
        """
        self.__ui_manager.add_ui_from_string(ui_description)

        actiongroup = Gtk.ActionGroup(name='mcomix-statusbar')
        actiongroup.add_toggle_actions([
            ('pagenumber', None, 'Show page numbers', None, None, self.toggle_status_visibility),
            ('filenumber', None, 'Show file numbers', None, None, self.toggle_status_visibility),
            ('resolution', None, 'Show resolution', None, None, self.toggle_status_visibility),
            ('rootpath', None, 'Show path', None, None, self.toggle_status_visibility),
            ('filename', None, 'Show filename', None, None, self.toggle_status_visibility),
            ('filesize', None, 'Show filesize', None, None, self.toggle_status_visibility),
            ('view mode', None, 'Show current mode', None, None, self.toggle_status_visibility)])
        self.__ui_manager.insert_action_group(actiongroup, 0)

        # Hook mouse release event
        self.connect('button-release-event', self._button_released)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)

        # Default status information
        self.__page_info = ''
        self.__file_info = ''
        self.__resolution = ''
        self.__root = ''
        self.__filename = ''
        self.__filesize = ''
        self.__view_mode = ''
        self._update_sensitivity()
        self.show_all()

        self.__loading = False

    def set_message(self, message: str):
        """
        Set a specific message (such as an error message) on the statusbar,
        replacing whatever was there earlier
        """

        self.__status.pop(0)
        self.__status.push(0, ' ' * self.__spacing + message)

    def set_page_number(self, page: int, total: int, this_screen: int):
        """
        Update the page number
        """

        p = ', '.join(str(page + i) for i in range(this_screen))
        self.__page_info = f'{p} / {total}'

    def get_page_number(self):
        """
        :returns: the bar's page information
        """

        return self.__page_info

    def set_mode(self):
        """
        Update the mode
        """

        if prefs['default manga mode']:
            self.__view_mode = 'Manga Mode'
        else:
            self.__view_mode = 'Western Mode'

    def set_file_number(self, fileno: int, total: int):
        """
        Updates the file number (i.e. number of current file/total files loaded)
        """

        if total > 0:
            self.__file_info = f'({fileno} / {total})'
        else:
            self.__file_info = ''

    def get_file_number(self):
        """
        Returns the bar's file information
        """

        return self.__file_info

    def set_resolution(self, dimensions: list):  # 2D only
        """
        Update the resolution data.
        Takes an iterable of tuples, (x, y, scale), describing the original
        resolution of an image as well as the currently displayed scale
        """

        self.__resolution = ', '.join(f'{d[0]}x{d[1]} ({d[2]:.2%})' for d in dimensions)

    def set_root(self, root: str):
        """
        Set the name of the root (directory or archive)
        """

        self.__root = root

    def set_filename(self, filename: str):
        """
        Update the filename
        """

        self.__filename = filename

    def set_filesize(self, size: str):
        """
        Update the filesize
        """

        if size is None:
            size = ''
        self.__filesize = size

    def update(self):
        """
        Set the statusbar to display the current state
        """

        s = f'{"|":^{self.__spacing + 2}}'
        text = s.join(self._get_status_text())
        self.__status.pop(0)
        self.__status.push(0, f'{"":>{self.__spacing}}{text}')

    def _get_status_text(self):
        """
        Returns an array of text fields that should be displayed
        """

        fields = [
            (constants.STATUS_PAGE, self.__page_info),
            (constants.STATUS_FILENUMBER, self.__file_info),
            (constants.STATUS_RESOLUTION, self.__resolution),
            (constants.STATUS_PATH, self.__root),
            (constants.STATUS_FILENAME, self.__filename),
            (constants.STATUS_FILESIZE, self.__filesize),
            (constants.STATUS_MODE, self.__view_mode),
        ]
        p = prefs['statusbar fields']

        return [s for c, s in filter(lambda f: f[0] & p, fields)]

    def toggle_status_visibility(self, action, *args):
        """
        Called when status entries visibility is to be changed
        """

        # Ignore events as long as control is still loading.
        if self.__loading:
            return

        names = {
            'pagenumber': constants.STATUS_PAGE,
            'resolution': constants.STATUS_RESOLUTION,
            'rootpath': constants.STATUS_PATH,
            'filename': constants.STATUS_FILENAME,
            'filenumber': constants.STATUS_FILENUMBER,
            'filesize': constants.STATUS_FILESIZE,
            'view mode': constants.STATUS_MODE,
        }

        bit = names[action.get_name()]

        if action.get_active():
            prefs['statusbar fields'] |= bit
        else:
            prefs['statusbar fields'] &= ~bit

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

        p = prefs['statusbar fields']
        names = {
            'pagenumber': p & constants.STATUS_PAGE,
            'filenumber': p & constants.STATUS_FILENUMBER,
            'resolution': p & constants.STATUS_RESOLUTION,
            'rootpath': p & constants.STATUS_PATH,
            'filename': p & constants.STATUS_FILENAME,
            'filesize': p & constants.STATUS_FILESIZE,
            'view mode': p & constants.STATUS_MODE,
        }

        for n, v in names.items():
            action = self.__ui_manager.get_action(f'/Statusbar/{n}')
            action.set_active(v)
