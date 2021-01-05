# -*- coding: utf-8 -*-

"""about_dialog.py - About dialog"""

import webbrowser

from gi.repository import Gtk

from mcomix.constants import Constants
from mcomix.icons import Icons


class AboutDialog(Gtk.AboutDialog):
    def __init__(self, window):
        super().__init__()

        self.set_transient_for(window)
        # self.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.set_name(Constants.APPNAME)
        self.set_program_name(Constants.APPNAME)
        self.set_version(f'Version {Constants.VERSION}')
        self.set_license_type(Gtk.License.GPL_2_0)
        self.set_website('https://github.com/thermitegod/mcomix-lite')
        self.set_website_label('Github')
        self.set_copyright('Copyright (C) 2005-2021')

        self.set_logo(Icons.load_icons())

        self.set_comments(f'{Constants.APPNAME} is an image viewer specifically designed to handle manga/comics. '
                          'It supports ZIP, 7Z, RAR, CBZ, CB7, CBR, and image files.')

        self.connect('activate-link', self._on_activate_link)

        self.show_all()

    @staticmethod
    def _on_activate_link(uri):
        webbrowser.open(uri)
        return True
