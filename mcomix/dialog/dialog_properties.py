# -*- coding: utf-8 -*-

from mcomix.dialog.dialog_base import DialogBase
from mcomix.properties_dialog import PropertiesDialog


class DialogProperties(DialogBase):
    def __init__(self):
        super().__init__()

    def open_dialog(self, window):
        """
        Create and display the given dialog
        """

        self.dialog = PropertiesDialog(window)
        self.dialog.connect('response', self.close_dialog)
