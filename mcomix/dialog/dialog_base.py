# -*- coding: utf-8 -*-


class DialogBase:

    __slots__ = ('dialog',)

    def __init__(self):
        super().__init__()

        self.dialog = None

    def open_dialog(self, window):
        """
        Create and display the given dialog
        """

        raise NotImplementedError

    def close_dialog(self, *args):
        """
        Destroy the dialog window if it exists
        """

        self.dialog.destroy()
