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

import mcomix.image_tools as image_tools


class PropertiesPage(Gtk.ScrolledWindow):
    """
    A page to put in the Gtk.Notebook. Contains info about a file, image, or archive.)
    """

    def __init__(self):
        super().__init__()

        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.__vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=12)
        self.add(self.__vbox)

        self.set_border_width(12)
        topbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=12)
        self.__vbox.pack_start(topbox, True, True, 0)
        self.__thumb = Gtk.Image()
        self.__thumb.set_size_request(128, 128)
        topbox.pack_start(self.__thumb, False, False, 0)
        borderbox = Gtk.Frame()
        borderbox.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        borderbox.set_size_request(-1, 130)
        topbox.pack_start(borderbox, True, True, 0)
        insidebox = Gtk.EventBox()
        insidebox.set_border_width(1)
        borderbox.add(insidebox)
        self.__insidebox = insidebox
        self.__mainbox = None
        self.__extrabox = None
        self.reset()

    def reset(self):
        self.__thumb.clear()
        if self.__mainbox is not None:
            self.__mainbox.destroy()
        self.__mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=5)
        self.__mainbox.set_border_width(10)
        self.__insidebox.add(self.__mainbox)
        if self.__extrabox is not None:
            self.__extrabox.destroy()
        self.__extrabox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        self.__vbox.pack_start(self.__extrabox, False, False, 0)

    def set_thumbnail(self, pixbuf):
        pixbuf = image_tools.add_border_pixbuf(pixbuf)
        self.__thumb.set_from_pixbuf(pixbuf)

    def set_filename(self, filename: str):
        """
        Set the filename to be displayed to <filename>. Call this before set_main_info()
        """

        label = Gtk.Label()
        label.set_markup(f'<b>{filename}</b>')
        label.set_xalign(0.0)
        label.set_yalign(0.5)
        label.set_selectable(True)
        label.set_line_wrap(True)
        self.__mainbox.pack_start(label, False, False, 0)
        self.__mainbox.pack_start(Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=True, spacing=0), True, True, 0)

    def set_main_info(self, info: tuple):
        """
        Set the information in the main info box (below the filename) to the values in the sequence <info>
        """

        for text in info:
            label = Gtk.Label(label=text)
            label.set_xalign(0.0)
            label.set_yalign(0.5)
            label.set_selectable(True)
            self.__mainbox.pack_start(label, False, False, 0)

    def set_secondary_info(self, info: tuple):
        """
        Set the information below the main info box to the values in the
        sequence <info>. Each entry in info should be a tuple (desc, value)
        """

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=True, spacing=8)
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=True, spacing=8)
        self.__extrabox.pack_start(left_box, False, False, 0)
        self.__extrabox.pack_start(right_box, False, False, 0)
        for desc, value in info:
            desc_label = Gtk.Label()
            desc_label.set_markup(f'<b>{desc}:</b>')
            desc_label.set_xalign(1.0)
            desc_label.set_yalign(1.0)
            left_box.pack_start(desc_label, True, True, 0)
            value_label = Gtk.Label(label=value)
            value_label.set_xalign(0.0)
            value_label.set_yalign(1.0)
            value_label.set_selectable(True)
            right_box.pack_start(value_label, True, True, 0)
