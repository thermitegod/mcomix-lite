# -*- coding: utf-8 -*-

"""dialog_handler.py - Takes care of opening and closing and destroying of simple dialog windows.
Dialog windows should only be taken care of here if they are windows that need to display
information and then exit with no added functionality inbetween"""

from mcomix.about_dialog import AboutDialog
from mcomix.properties_dialog import PropertiesDialog


class _DialogHandler:
    def __init__(self):
        super().__init__()
        self.__dialog_windows = {'about-dialog': [None, AboutDialog],
                                 'properties-dialog': [None, PropertiesDialog]}

    def open_dialog(self, action, data: tuple):
        """
        Create and display the given dialog
        """

        window, name_of_dialog = data

        # if the dialog window is not created then create the window
        # and connect the _close_dialog action to the dialog window
        dialog = self.__dialog_windows[name_of_dialog]
        if dialog[0] is None:
            self.__dialog_windows[name_of_dialog][0] = dialog[1](window)
            self.__dialog_windows[name_of_dialog][0].connect('response', self.close_dialog, name_of_dialog)
        else:
            # if the dialog window already exists bring it to the forefront of the screen
            dialog[0].present()

    def close_dialog(self, action, exit_response: int, name_of_dialog: str):
        # if the dialog window exists then destroy it
        dialog = self.__dialog_windows[name_of_dialog]
        if dialog[0] is not None:
            dialog[0].destroy()
            dialog[0] = None


DialogHandler = _DialogHandler()
