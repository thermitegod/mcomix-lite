# -*- coding: utf-8 -*-

from __future__ import annotations

from mcomix.about_dialog import AboutDialog
from mcomix.enhance_dialog import EnhanceImageDialog
from mcomix.file_chooser import FileChooser
from mcomix.keybindings_dialog import KeybindingEditorDialog
from mcomix.preferences_dialog import PreferencesDialog
from mcomix.properties_dialog import PropertiesDialog


class DialogChooser:

    __slots__ = ('__dialog', '__dialog_chosen')

    def __init__(self, dialog: str):
        super().__init__()

        self.__dialog = None
        self.__dialog_chosen = None

        match dialog:
            case 'about':
                self.__dialog_chosen = AboutDialog
            case 'enhance':
                self.__dialog_chosen = EnhanceImageDialog
            case 'file_chooser':
                self.__dialog_chosen = FileChooser
            case 'keybindings':
                self.__dialog_chosen = KeybindingEditorDialog
            case 'preferences':
                self.__dialog_chosen = PreferencesDialog
            case 'properties':
                self.__dialog_chosen = PropertiesDialog
            case _:
                raise ValueError

    def open_dialog(self, window):
        """
        Create and display the given dialog
        """

        self.__dialog = self.__dialog_chosen(window)
        self.__dialog.connect('response', self.close_dialog)

    def close_dialog(self, *args):
        """
        Destroy the dialog window if it exists
        """

        self.__dialog.destroy()
