# -*- coding: utf-8 -*-

from __future__ import annotations

from gi.repository import Gtk

from mcomix.keybindings_editor import KeybindingEditorWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class KeybindingEditorDialog(Gtk.Dialog):
    __slots__ = ('__window', '__shortcuts')

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
