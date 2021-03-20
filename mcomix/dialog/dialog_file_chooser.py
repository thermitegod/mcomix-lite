# -*- coding: utf-8 -*-

from mcomix.dialog.dialog_base import DialogBase
from mcomix.file_chooser import FileChooser


class DialogFileChooser(DialogBase):
    def __init__(self):
        super().__init__()

    def open_dialog(self, window):
        """
        Create and display the preference dialog
        """

        self.dialog = FileChooser(window)
        self.dialog.connect('response', self.close_dialog)
