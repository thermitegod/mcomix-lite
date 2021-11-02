# -*- coding: utf-8 -*-

from mcomix.dialog.dialog_base import DialogBase
from mcomix.keybindings_dialog import KeybindingEditorDialog


class DialogKeybindings(DialogBase):
    __slots__ = ()

    def __init__(self):
        super().__init__()

    def open_dialog(self, window):
        """
        Create and display the preference dialog
        """

        self.dialog = KeybindingEditorDialog(window)
