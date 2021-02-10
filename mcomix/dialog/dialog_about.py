# -*- coding: utf-8 -*-

from mcomix.about_dialog import AboutDialog
from mcomix.dialog.dialog_base import DialogBase


class DialogAbout(DialogBase):
    def __init__(self):
        super().__init__()

    def open_dialog(self, event, data: tuple):
        """
        Create and display the given dialog
        """

        self.dialog = AboutDialog(data.window)
        self.dialog.connect('response', self.close_dialog)
