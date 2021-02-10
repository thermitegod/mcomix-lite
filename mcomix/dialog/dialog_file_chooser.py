# -*- coding: utf-8 -*-

from mcomix.dialog.dialog_base import DialogBase
from mcomix.file_chooser_main_dialog import _MainFileChooserDialog


class DialogFileChooser(DialogBase):
    def __init__(self):
        super().__init__()

    def open_dialog(self, event, data: tuple):
        """
        Create and display the preference dialog
        """

        self.dialog = _MainFileChooserDialog(data.window)
        self.dialog.connect('response', self.close_dialog)
