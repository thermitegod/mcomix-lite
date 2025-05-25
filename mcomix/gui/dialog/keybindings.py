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

from gi.repository import Gtk

from mcomix.gui.dialog.keybindings_editor import KeybindingEditorWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.gui.main_window import MainWindow


class KeybindingEditorDialog(Gtk.Dialog):
    def __init__(self, window: MainWindow):
        super().__init__(title='Preferences')

        self.__window = window

        self.set_modal(True)
        self.set_transient_for(window)

        self.set_size_request(800, 800)

        self.add_button('_Reset keys', Gtk.ResponseType.REJECT)
        self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.set_resizable(True)
        self.set_default_response(Gtk.ResponseType.CLOSE)

        self.connect('response', self._response)

        notebook = Gtk.Notebook()
        self.vbox.pack_start(notebook, True, True, 0)
        self.set_border_width(2)
        notebook.set_border_width(2)

        self.__shortcuts = self._init_shortcuts_tab()
        notebook.append_page(self.__shortcuts,
                             Gtk.Label(label='Keybindings'))

        self.show_all()

    def _init_shortcuts_tab(self):
        # ----------------------------------------------------------------
        # The "Shortcuts" tab.
        # ----------------------------------------------------------------
        page = KeybindingEditorWindow(self.__window)

        return page

    def _response(self, dialog, response):
        match response:
            case Gtk.ResponseType.REJECT:
                self.__window.keybindings.reset_keybindings()
                self.__window.keybindings.write_keybindings_file()
                self.__shortcuts.refresh_model()

            case _:
                self.destroy()
