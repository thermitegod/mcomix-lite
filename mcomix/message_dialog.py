# -*- coding: utf-8 -*-

"""Simple extension of Gtk.MessageDialog for consistent formating. Also supports remembering the dialog result"""

import html

from gi.repository import Gtk

from mcomix.preferences import config


class MessageDialog(Gtk.MessageDialog):
    __slots__ = ('__dialog_id', '__choices', '__remember_checkbox')

    def __init__(self, window, flags: int = 0, message_type: int = 0, buttons: int = 0):
        """
        Creates a dialog window.

        :param window: Parent window
        :param flags: Dialog flags
        :param type: Dialog icon/type
        :param buttons: Dialog buttons. Can only be a predefined BUTTONS_XXX constant
        """

        super().__init__(
            message_type=message_type, buttons=buttons,
            modal=flags & Gtk.DialogFlags.MODAL,
            destroy_with_parent=flags & Gtk.DialogFlags.DESTROY_WITH_PARENT,
        )

        self.set_modal(True)
        self.set_transient_for(window)

        #: Unique dialog identifier (for storing 'Do not ask again')
        self.__dialog_id = None
        #: List of response IDs that should be remembered
        self.__choices = []
        #: Automatically destroy dialog after run?
        self.__auto_destroy = True

        self.__remember_checkbox = Gtk.CheckButton(label='Do not ask again.')
        self.__remember_checkbox.set_no_show_all(True)
        self.__remember_checkbox.set_can_focus(False)
        self.get_message_area().pack_end(self.__remember_checkbox, True, True, 6)

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

        if self.__auto_destroy:
            self.destroy()
        return result
