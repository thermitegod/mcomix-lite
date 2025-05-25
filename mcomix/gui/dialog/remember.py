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

from mcomix.preferences import config


class MessageDialogRemember(Gtk.MessageDialog):
    def __init__(self):
        """
        Creates a dialog window.
        """

        super().__init__()

        self.set_modal(True)

        #: Unique dialog identifier (for storing 'Do not ask again')
        self.__dialog_id = None
        #: List of response IDs that should be remembered
        self.__choices = []

        self.__remember_checkbox = Gtk.CheckButton(label='Do not ask again.')
        self.__remember_checkbox.set_no_show_all(True)
        self.__remember_checkbox.set_can_focus(False)
        self.get_message_area().pack_end(self.__remember_checkbox, True, True, 6)

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

    def should_remember_choice(self):
        """
        :returns: True when the dialog choice should be remembered
        """

        return self.__remember_checkbox.get_active()

    def set_should_remember_choice(self, dialog_id: str, choices: tuple):
        """
        This method enables the 'Do not ask again' checkbox.

        :param dialog_id: Unique identifier for the dialog (a string).
        :param choices: List of response IDs that should be remembered
        """

        self.__remember_checkbox.show()
        self.__dialog_id = dialog_id
        self.__choices = [int(choice) for choice in choices]

    def run(self):
        """
        Makes the dialog visible and waits for a result. Also destroys
        the dialog after the result has been returned
        """

        if self.__dialog_id in config['STORED_DIALOG_CHOICES']:
            self.destroy()
            return config['STORED_DIALOG_CHOICES'][self.__dialog_id]

        self.show_all()
        # Prevent checkbox from grabbing focus by only enabling it after show
        self.__remember_checkbox.set_can_focus(True)

        result = super().run()

        if self.should_remember_choice() and int(result) in self.__choices:
            config['STORED_DIALOG_CHOICES'][self.__dialog_id] = int(result)

        self.destroy()
        return result
