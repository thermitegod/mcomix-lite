# -*- coding: utf-8 -*-

"""menubar.py - creates the menubar for main window"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from gi.repository import Gtk

from mcomix.bookmark_menu import BookmarksMenu
from mcomix.file_handler import FileHandler

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class Menubar(Gtk.EventBox):
    __slots__ = ()

    def __init__(self, window: MainWindow):
        super().__init__()

        file_handler = FileHandler(None)

        menubar = Gtk.MenuBar()
        self.add(menubar)

        @dataclass(frozen=True)
        class MENUBAR:
            __slots__ = ('label', 'create_function', 'callback')
            label: str
            create_function: Callable
            callback: Callable

        # File #
        menu_file = Gtk.Menu()
        menuitem_file = Gtk.MenuItem(label='File')
        menuitem_file.set_submenu(menu_file)

        memu_file_items = (
            MENUBAR('Open', self._create_submenu_item, window.open_dialog_file_chooser),
            MENUBAR('separator', self._create_separator, None),
            MENUBAR('Save Page As', self._create_submenu_item, window.extract_page),
            MENUBAR('Refresh', self._create_submenu_item, file_handler.refresh_file),
            MENUBAR('Properties', self._create_submenu_item, window.open_dialog_properties),
            MENUBAR('separator', self._create_separator, None),
            MENUBAR('Trash', self._create_submenu_item, window.trash_file),
            MENUBAR('separator', self._create_separator, None),
            MENUBAR('Minimize', self._create_submenu_item, window.minimize),
            MENUBAR('Close', self._create_submenu_item, file_handler.close_file),
            MENUBAR('Quit', self._create_submenu_item, window.terminate_program),
        )

        self._populate_menu(items=memu_file_items, menu=menu_file)
        menubar.append(menuitem_file)

        # Edit #
        menu_edit = Gtk.Menu()
        menuitem_edit = Gtk.MenuItem(label='Edit')
        menuitem_edit.set_submenu(menu_edit)

        memu_edit_items = (
            MENUBAR('Preference', self._create_submenu_item, window.open_dialog_preference),
            MENUBAR('Keybindings', self._create_submenu_item, window.open_dialog_keybindings),
        )

        self._populate_menu(items=memu_edit_items, menu=menu_edit)
        menubar.append(menuitem_edit)

        # View #
        menu_view = Gtk.Menu()
        menuitem_view = Gtk.MenuItem(label='View')
        menuitem_view.set_submenu(menu_view)

        memu_edit_items = (
            MENUBAR('Stretch Small Images', self._create_submenu_item, window.change_stretch),
            MENUBAR('separator', self._create_separator, None),
            MENUBAR('Best Fit Mode', self._create_submenu_item, window.change_fit_mode_best),
            MENUBAR('Fit Width Mode', self._create_submenu_item, window.change_fit_mode_width),
            MENUBAR('Fit Height Mode', self._create_submenu_item, window.change_fit_mode_height),
            MENUBAR('Fit Size Mode', self._create_submenu_item, window.change_fit_mode_size),
            MENUBAR('Manual Zoom Mode', self._create_submenu_item, window.change_fit_mode_manual),
        )

        self._populate_menu(items=memu_edit_items, menu=menu_view)
        menubar.append(menuitem_view)

        # Bookmarks #
        menuitem_bookmarks = Gtk.MenuItem(label='Bookmarks')
        bookmarks = BookmarksMenu(window)
        menuitem_bookmarks.set_submenu(bookmarks)

        menubar.append(menuitem_bookmarks)

        # Tools #
        menu_tools = Gtk.Menu()
        menuitem_tools = Gtk.MenuItem(label='Tools')
        menuitem_tools.set_submenu(menu_tools)

        memu_tools_items = (
            MENUBAR('Enhance Image', self._create_submenu_item, window.open_dialog_enhance),
            MENUBAR('separator', self._create_separator, None),
            MENUBAR('Rotate 90°', self._create_submenu_item, window.rotate_90),
            MENUBAR('Rotate 180°', self._create_submenu_item, window.rotate_180),
            MENUBAR('Rotate 270°', self._create_submenu_item, window.rotate_270),
        )

        self._populate_menu(items=memu_tools_items, menu=menu_tools)
        menubar.append(menuitem_tools)

        # Help #
        menu_help = Gtk.Menu()
        menuitem_help = Gtk.MenuItem(label='Help')
        menuitem_help.set_submenu(menu_help)

        memu_help_items = (
            MENUBAR('About', self._create_submenu_item, window.open_dialog_about),
        )

        self._populate_menu(items=memu_help_items, menu=menu_help)
        menubar.append(menuitem_help)

        #
        self.show_all()

    def _populate_menu(self, items: tuple, menu):
        for item in items:
            item.create_function(menu, item.label, item.callback)

    def _create_submenu_item(self, menu, label: str, callback: Callable):
        item = Gtk.MenuItem()
        item.set_label(label)
        item.connect('activate', callback)
        menu.append(item)

    def _create_separator(self, menu, *args):
        menu.append(Gtk.SeparatorMenuItem())
