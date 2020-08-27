# -*- coding: utf-8 -*-

"""dialog_handler.py - Takes care of opening and closing and destroying of simple dialog windows.
Dialog windows should only be taken care of here if they are windows that need to display
information and then exit with no added functionality inbetween"""

from mcomix import about_dialog, properties_dialog

dialog_windows = {'about-dialog': [None, about_dialog.AboutDialog],
                  'properties-dialog': [None, properties_dialog.PropertiesDialog]}


def open_dialog(action, data: tuple):
    """
    Create and display the given dialog
    """

    window, name_of_dialog = data

    # if the dialog window is not created then create the window
    # and connect the _close_dialog action to the dialog window
    if (_dialog := dialog_windows[name_of_dialog])[0] is None:
        dialog_windows[name_of_dialog][0] = _dialog[1](window)
        dialog_windows[name_of_dialog][0].connect('response', _close_dialog, name_of_dialog)
    else:
        # if the dialog window already exists bring it to the forefront of the screen
        _dialog[0].present()


def _close_dialog(action, exit_response: int, name_of_dialog: str):
    # if the dialog window exists then destroy it
    if (_dialog := dialog_windows[name_of_dialog])[0] is not None:
        _dialog[0].destroy()
        _dialog[0] = None
