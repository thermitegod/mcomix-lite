# -*- coding: utf-8 -*-

from __future__ import annotations

from enum import Enum, auto

from mcomix.about_dialog import AboutDialog
from mcomix.enhance_dialog import EnhanceImageDialog
from mcomix.file_chooser import FileChooser
from mcomix.keybindings_dialog import KeybindingEditorDialog
from mcomix.preferences_dialog import PreferencesDialog
from mcomix.properties_dialog import PropertiesDialog


class DialogChoice(Enum):
    ABOUT = auto()
    ENHANCE = auto()
    FILECHOOSER = auto()
    KEYBINDINGS = auto()
    PREFERENCES = auto()
    PROPERTIES = auto()


class DialogChooser:

    __slots__ = ('__dialog', '__dialog_chosen')

    def __init__(self, dialog: str):
        super().__init__()

        self.__dialog = None

        match dialog:
            case DialogChoice.ABOUT:
                self.__dialog_chosen = AboutDialog
            case DialogChoice.ENHANCE:
                self.__dialog_chosen = EnhanceImageDialog
            case DialogChoice.FILECHOOSER:
                self.__dialog_chosen = FileChooser
            case DialogChoice.KEYBINDINGS:
                self.__dialog_chosen = KeybindingEditorDialog
            case DialogChoice.PREFERENCES:
                self.__dialog_chosen = PreferencesDialog
            case DialogChoice.PROPERTIES:
                self.__dialog_chosen = PropertiesDialog

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
