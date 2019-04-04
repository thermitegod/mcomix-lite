# -*- coding: utf-8 -*-

"""about_dialog.py - About dialog"""

import webbrowser

from gi.repository import Gtk
from importlib import resources

from mcomix import constants, image_tools


class _AboutDialog(Gtk.AboutDialog):
    def __init__(self, window):
        super(_AboutDialog, self).__init__()
        self.set_transient_for(window)
        # self.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.set_name(constants.APPNAME)
        self.set_program_name(constants.APPNAME)
        self.set_version('Version ' + constants.VERSION)
        self.set_license_type(Gtk.License.GPL_2_0,)
        self.set_website('https://github.com/thermitegod/mcomix-lite')
        self.set_website_label('Github')
        self.set_copyright('Copyright (C) 2005-2016')

        icon_data = resources.read_binary('mcomix.images', 'mcomix.png')
        pixbuf = image_tools.load_pixbuf_data(icon_data)
        self.set_logo(pixbuf)

        self.set_comments('%s is an image viewer specifically designed to handle manga/comics. ' % constants.APPNAME +
                          'It reads ZIP, 7Z, RAR, CBZ, CB7, CBR, PDF, LHA, and image files.')

        self.connect('activate-link', self._on_activate_link)

        self.show_all()

    @staticmethod
    def _on_activate_link(uri):
        webbrowser.open(uri)
        return True
