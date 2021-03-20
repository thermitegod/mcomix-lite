# -*- coding: utf-8 -*-

from mcomix.dialog.dialog_base import DialogBase
from mcomix.enhance_dialog import EnhanceImageDialog


class DialogEnhance(DialogBase):
    def __init__(self):
        super().__init__()

    def open_dialog(self, window):
        """
        Create and display the (singleton) image enhancement dialog
        """

        self.dialog = EnhanceImageDialog(window)
        self.dialog.connect('response', self.close_dialog)
