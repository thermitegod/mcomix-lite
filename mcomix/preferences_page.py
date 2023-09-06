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

from gi.repository import Gtk

from mcomix.preferences_section import PreferenceSection


class PreferencePage(Gtk.VBox):
    """
    The _PreferencePage is a conveniece class for making one "page"
    in a preferences-style dialog that contains one or more _PreferenceSections
    """

    def __init__(self, right_column_width: int = None):
        """
        Create a new page where any possible right columns have the width request <right_column_width>
        """

        super().__init__(homogeneous=False, spacing=12)

        self.set_border_width(12)
        self.__right_column_width = right_column_width
        self.__section = None

    def new_section(self, header):
        """
        Start a new section in the page, with the header text from <header>
        """

        self.__section = PreferenceSection(header, self.__right_column_width)
        self.pack_start(self.__section, False, False, 0)

    def add_row(self, left_item, right_item=None):
        """
        Add a row to the page (in the latest section), containing one
        or two items. If the left item is a label it is automatically
        aligned properly
        """

        if isinstance(left_item, Gtk.Label):
            left_item.set_xalign(0.0)
            left_item.set_yalign(0.5)

        if right_item is None:
            self.__section.get_contentbox().pack_start(left_item, True, True, 0)
        else:
            left_box, right_box = self.__section.new_split_vboxes()
            left_box.pack_start(left_item, True, True, 0)
            right_box.pack_start(right_item, True, True, 0)
