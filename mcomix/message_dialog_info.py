# -*- coding: utf-8 -*-

from gi.repository import Gtk

from mcomix.message_dialog import MessageDialog


class MessageDialogInfo:
    __slots__ = ()

    def __init__(self, window, primary: str = None, secondary: str = None):
        """
        Creates a dialog window that only shows a message.

        :param primary: Main text.
        :param secondary: Descriptive text
        """

        super().__init__()

        dialog = MessageDialog(
            window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE)
        dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_text(primary=primary, secondary=secondary)
        dialog.run()
