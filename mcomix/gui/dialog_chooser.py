# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from mcomix.gui.dialog.about import AboutDialog
from mcomix.gui.dialog.file_chooser import FileChooser
from mcomix.gui.dialog.keybindings import KeybindingEditorDialog
from mcomix.gui.dialog.preferences import PreferencesDialog
from mcomix.gui.dialog.properties import PropertiesDialog

from mcomix_compiled import DialogChoice

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.gui.main_window import MainWindow


class DialogChooser:
    def __init__(self, dialog: str):
        super().__init__()

        self.__dialog = None

        match dialog:
            case DialogChoice.ABOUT:
                self.__dialog_chosen = AboutDialog
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
