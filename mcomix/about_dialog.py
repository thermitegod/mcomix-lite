# -*- coding: utf-8 -*-

"""about_dialog.py - About dialog"""

from __future__ import annotations

from pathlib import Path

from gi.repository import Gtk, GdkPixbuf

from mcomix.enums import Mcomix
from mcomix.image_tools import ImageTools

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class AboutDialog(Gtk.AboutDialog):
    def __init__(self, window: MainWindow):
        super().__init__(title='About')

        self.__window = window

        self.set_modal(True)
        self.set_transient_for(self.__window)

        self.set_titlebar(Gtk.HeaderBar(title='About'))

        logo = Path(__file__).parent / 'images' / 'mcomix.png'
        self.set_logo(GdkPixbuf.Pixbuf.new_from_file(str(logo)))

        self.set_name(Mcomix.APP_NAME.value)
        self.set_program_name(Mcomix.APP_NAME.value)
        self.set_version(f'Version {Mcomix.VERSION.value}')
        self.set_copyright('Copyright (C) 2005-2023')

        self.set_license_type(Gtk.License.GPL_2_0)

        link = f'https://github.com/thermitegod/{Mcomix.PROG_NAME.value}'
        self.set_website(link)
        self.set_website_label(link)

        self.set_comments(f'{Mcomix.APP_NAME.value} is an image viewer specifically designed '
                          f'to handle manga, comics, and image files.')

        self.show_all()
