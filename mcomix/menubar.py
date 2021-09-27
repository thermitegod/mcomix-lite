# -*- coding: utf-8 -*-

"""menubar.py - creates the menubar for main window"""

from dataclasses import dataclass
from typing import Callable

from gi.repository import Gtk

from mcomix.bookmark_menu import BookmarksMenu


class Menubar(Gtk.EventBox):
    def __init__(self, window):
        super().__init__()

        self.__window = window

        self.__menubar = Gtk.MenuBar()
        self.add(self.__menubar)

        @dataclass(frozen=True)
        class MENUBAR:
            __slots__ = ['label', 'create_function', 'callback']
            label: str
            create_function: Callable
            callback: Callable

        # File #
        menu_file = Gtk.Menu()
        menuitem_file = Gtk.MenuItem(label='File')
        menuitem_file.set_submenu(menu_file)

        memu_file_items = (
            MENUBAR('Open', self._create_submenu_item, self.__window.open_dialog_file_chooser),
            MENUBAR('separator', self._create_separator, None),
            MENUBAR('Save Page As', self._create_submenu_item, self.__window.extract_page),
            MENUBAR('Refresh', self._create_submenu_item, self.__window.filehandler.refresh_file),
            MENUBAR('Properties', self._create_submenu_item, self.__window.open_dialog_properties),
            MENUBAR('separator', self._create_separator, None),
            MENUBAR('Trash', self._create_submenu_item, self.__window.trash_file),
            MENUBAR('separator', self._create_separator, None),
            MENUBAR('Minimize', self._create_submenu_item, self.__window.minimize),
            MENUBAR('Close', self._create_submenu_item, self.__window.filehandler.close_file),
            MENUBAR('Quit', self._create_submenu_item, self.__window.terminate_program),
        )

        self._populate_menu(items=memu_file_items, menu=menu_file)
        self.__menubar.append(menuitem_file)

        # Edit #
        menu_edit = Gtk.Menu()
        menuitem_edit = Gtk.MenuItem(label='Edit')
        menuitem_edit.set_submenu(menu_edit)

        memu_edit_items = (
            MENUBAR('Preference', self._create_submenu_item, self.__window.open_dialog_preference),
        )

        self._populate_menu(items=memu_edit_items, menu=menu_edit)
        self.__menubar.append(menuitem_edit)

        # View #
        menu_view = Gtk.Menu()
        menuitem_view = Gtk.MenuItem(label='View')
        menuitem_view.set_submenu(menu_view)

        memu_edit_items = (
            MENUBAR('Stretch Small Images', self._create_submenu_item, self.__window.change_stretch),
            MENUBAR('separator', self._create_separator, None),
            MENUBAR('Best Fit Mode', self._create_submenu_item, self.__window.change_fit_mode_best),
            MENUBAR('Fit Width Mode', self._create_submenu_item, self.__window.change_fit_mode_width),
            MENUBAR('Fit Height Mode', self._create_submenu_item, self.__window.change_fit_mode_height),
            MENUBAR('Fit Size Mode', self._create_submenu_item, self.__window.change_fit_mode_size),
            MENUBAR('Manual Zoom Mode', self._create_submenu_item, self.__window.change_fit_mode_manual),
        )

        self._populate_menu(items=memu_edit_items, menu=menu_view)
        self.__menubar.append(menuitem_view)

        # Bookmarks #
        menuitem_bookmarks = Gtk.MenuItem(label='Bookmarks')
        bookmarks = BookmarksMenu(self.__window)
        menuitem_bookmarks.set_submenu(bookmarks)

        self.__menubar.append(menuitem_bookmarks)

        # Tools #
        menu_tools = Gtk.Menu()
        menuitem_tools = Gtk.MenuItem(label='Tools')
        menuitem_tools.set_submenu(menu_tools)

        memu_tools_items = (
            MENUBAR('Enhance Image', self._create_submenu_item, self.__window.open_dialog_enhance),
            MENUBAR('separator', self._create_separator, None),
            MENUBAR('Rotate 90°', self._create_submenu_item, self.__window.rotate_90),
            MENUBAR('Rotate 180°', self._create_submenu_item, self.__window.rotate_180),
            MENUBAR('Rotate 270°', self._create_submenu_item, self.__window.rotate_270),
        )

        self._populate_menu(items=memu_tools_items, menu=menu_tools)
        self.__menubar.append(menuitem_tools)

        # Help #
        menu_help = Gtk.Menu()
        menuitem_help = Gtk.MenuItem(label='Help')
        menuitem_help.set_submenu(menu_help)

        memu_help_items = (
            MENUBAR('About', self._create_submenu_item, self.__window.open_dialog_about),
        )

        self._populate_menu(items=memu_help_items, menu=menu_help)
        self.__menubar.append(menuitem_help)

        #
        self.show_all()

    @staticmethod
    def _populate_menu(items: tuple, menu):
        for item in items:
            item.create_function(menu, item.label, item.callback)

    @staticmethod
    def _create_submenu_item(menu, label: str, callback: Callable):
        item = Gtk.MenuItem()
        item.set_label(label)
        item.connect('activate', callback)
        menu.append(item)

    @staticmethod
    def _create_separator(menu, *args):
        menu.append(Gtk.SeparatorMenuItem())
