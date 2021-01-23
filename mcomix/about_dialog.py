# -*- coding: utf-8 -*-

"""about_dialog.py - About dialog"""

import webbrowser

from gi.repository import Gtk

from mcomix.constants import Constants


class AboutDialog(Gtk.AboutDialog):
    def __init__(self, window):
        super().__init__()

        self.__window = window

        self.set_transient_for(self.__window)
        # self.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.set_name(Constants.APPNAME)
        self.set_program_name(Constants.APPNAME)
        self.set_version(f'Version {Constants.VERSION}')
        self.set_license_type(Gtk.License.GPL_2_0)
        self.set_website(f'https://github.com/thermitegod/{Constants.PROG_NAME}')
        self.set_website_label('Github')
        self.set_copyright('Copyright (C) 2005-2021')

        self.set_logo(self.__window.icons.load_icons())

        self.set_comments(f'{Constants.APPNAME} is an image viewer specifically designed '
                          f'to handle manga, comics, and image files.')

        self.connect('activate-link', self._on_activate_link)

        self.show_all()

    @staticmethod
    def _on_activate_link(obj, url):
        webbrowser.open(url)
