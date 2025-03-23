# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from pathlib import Path

from gi.repository import Gtk

import mcomix.image_tools as image_tools

from mcomix_compiled import PackageInfo

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

        pixbuf_logo = image_tools.load_pixbuf(logo, force_static=True)
        if pixbuf_logo is not None:
            self.set_logo(pixbuf_logo)

        self.set_name(PackageInfo.APP_NAME)
        self.set_program_name(PackageInfo.APP_NAME)
        self.set_version(f'Version {PackageInfo.VERSION}')
        self.set_copyright('Copyright (C) 2005-2023')

        self.set_license_type(Gtk.License.GPL_2_0)

        link = f'https://github.com/thermitegod/{PackageInfo.PROG_NAME}'
        self.set_website(link)
        self.set_website_label(link)

        self.set_comments(f'{PackageInfo.APP_NAME} is an image viewer specifically designed '
                          f'to handle manga, comics, and image files.')

        self.show_all()
