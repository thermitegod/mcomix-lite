# -*- coding: utf-8 -*-

"""about_dialog.py - About dialog."""

import webbrowser
import pkg_resources

from gi.repository import Gtk

from mcomix import constants, image_tools


class _AboutDialog(Gtk.AboutDialog):
    def __init__(self, window):
        super(_AboutDialog, self).__init__()
        self.set_transient_for(window)

        self.set_name(constants.APPNAME)
        self.set_program_name(constants.APPNAME)
        self.set_version(constants.VERSION)
        self.set_license_type(Gtk.License.GPL_2_0,)
        self.set_website('https://github.com/thermitegod/mcomix-lite')
        # self.set_website_label('https://github.com/thermitegod/mcomix-lite')
        self.set_copyright('Copyright (C) 2005-2016')

        icon_data = pkg_resources.resource_string(__package__, 'images/mcomix.png')
        pixbuf = image_tools.load_pixbuf_data(icon_data)
        self.set_logo(pixbuf)

        self.set_comments('%s is an image viewer specifically designed to handle manga/comics. ' % constants.APPNAME +
                          'It reads 7Z, ZIP, RAR, PDF, LHA, and plain image files.')

        self.connect('activate-link', self._on_activate_link)

        self.show_all()

    @staticmethod
    def _on_activate_link(uri):
        webbrowser.open(uri)
        return True
