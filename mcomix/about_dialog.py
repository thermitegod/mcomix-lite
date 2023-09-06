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

from gi.repository import Gtk, GdkPixbuf

from mcomix.enums import Mcomix

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
