# -*- coding: utf-8 -*-

from __future__ import annotations

from mcomix.about_dialog import AboutDialog
from mcomix.enhance_dialog import EnhanceImageDialog
from mcomix.enums import DialogChoice
from mcomix.file_chooser import FileChooser
from mcomix.keybindings_dialog import KeybindingEditorDialog
from mcomix.preferences_dialog import PreferencesDialog
from mcomix.properties_dialog import PropertiesDialog

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class DialogChooser:
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

    def open_dialog(self, window: MainWindow):
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
