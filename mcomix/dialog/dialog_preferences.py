# -*- coding: utf-8 -*-

from mcomix.dialog.dialog_base import DialogBase
from mcomix.preferences_dialog import PreferencesDialog


class DialogPreference(DialogBase):
    def __init__(self):
        super().__init__()

    def open_dialog(self, event, window):
        """
        Create and display the preference dialog
        """

        self.dialog = PreferencesDialog(window)
