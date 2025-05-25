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

import html

from gi.repository import Gtk


class MessageDialogInfo(Gtk.MessageDialog):
    def __init__(self):
        """
        Creates a dialog window that only shows a message.

        :param primary: Main text.
        :param secondary: Descriptive text
        """

        super().__init__()

        self.set_modal(True)

        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

    def set_text(self, primary: str, secondary: str = None):
        """
        Formats the dialog's text fields.

        :param primary: Main text.
        :param secondary: Descriptive text
        """

        self.set_markup(f'<span weight="bold" size="larger">{html.escape(primary)}</span>')

        if secondary:
            self.format_secondary_markup(html.escape(secondary))

    def run(self):
        """
        Makes the dialog visible and waits for a result. Also destroys
        the dialog after the result has been returned
        """

        self.show_all()
        result = super().run()
        self.destroy()
        return result
