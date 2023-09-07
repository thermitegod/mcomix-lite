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


class PreferenceSection(Gtk.Box):
    """
    The _PreferenceSection is a convenience class for making one
    "section" of a preference-style dialog, e.g. it has a bold header
    and a number of rows which are indented with respect to that header
    """

    def __init__(self, header, right_column_width: int = None):
        """
        Contruct a new section with the header set to the text in
        <header>, and the width request of the (possible) right columns
        set to that of <right_column_width>
        """

        super().__init__(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)

        self.__right_column_width = right_column_width
        self.__contentbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=6)
        label = Gtk.Label()
        label.set_markup(f'<b>{header}</b>')
        label.set_xalign(0.0)
        label.set_yalign(0.5)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=0)
        hbox.pack_start(Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=True, spacing=0), False, False, 6)
        hbox.pack_start(self.__contentbox, True, True, 0)
        self.pack_start(label, False, False, 0)
        self.pack_start(hbox, False, False, 6)

    def new_split_vboxes(self):
        """
        Return two new VBoxes that are automatically put in the section
        after the previously added items. The right one has a width request
        equal to the right_column_width value passed to the class contructor,
        in order to make it easy for  all "right column items" in a page to
        line up nicely
        """

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=6)
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=6)

        if self.__right_column_width is not None:
            right_box.set_size_request(self.__right_column_width, -1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=12)
        hbox.pack_start(left_box, True, True, 0)
        hbox.pack_start(right_box, False, False, 0)
        self.__contentbox.pack_start(hbox, True, True, 0)
        return left_box, right_box

    def get_contentbox(self):
        return self.__contentbox
