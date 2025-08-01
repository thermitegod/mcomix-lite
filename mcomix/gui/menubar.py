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

from dataclasses import dataclass
from typing import Callable

from gi.repository import Gtk

from mcomix.gui.bookmark_menu import BookmarksMenu
from mcomix.lib.events import Events, EventType

from mcomix_compiled import ZoomModes

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.gui.main_window import MainWindow


class Menubar(Gtk.EventBox):
    def __init__(self, window: MainWindow):
        super().__init__()

        events = Events()

        menubar = Gtk.MenuBar()
        self.add(menubar)

        @dataclass(frozen=True)
        class MENUBAR:
            label: str
            create_function: Callable
            event: Callable
            event_type: EventType
            event_kwargs: dict

        # File #
        menu_file = Gtk.Menu()
        menuitem_file = Gtk.MenuItem(label='File')
        menuitem_file.set_submenu(menu_file)

        memu_file_items = (
            MENUBAR('Open', self._create_submenu_item, events.run_events_gui, EventType.KB_OPEN_DIALOG_FILECHOOSER, None,),
            MENUBAR('separator', self._create_separator, None, None, None),
            MENUBAR('Save Page As', self._create_submenu_item, events.run_events_gui, EventType.KB_EXTRACT_PAGE, None),
            MENUBAR('Refresh', self._create_submenu_item, events.run_events_gui, EventType.KB_FILE_REFRESH, None),
            MENUBAR('Properties', self._create_submenu_item, events.run_events_gui, EventType.KB_OPEN_DIALOG_PROPERTIES, None,),
            MENUBAR('separator', self._create_separator, None, None, None),
            MENUBAR('Trash', self._create_submenu_item, events.run_events_gui, EventType.KB_FILE_TRASH, None),
            MENUBAR('separator', self._create_separator, None, None, None),
            MENUBAR('Minimize', self._create_submenu_item, events.run_events_gui, EventType.KB_MINIMIZE, None),
            MENUBAR('Close', self._create_submenu_item, events.run_events_gui, EventType.KB_FILE_CLOSE, None),
            MENUBAR('Quit', self._create_submenu_item, events.run_events_gui, EventType.KB_EXIT, None),
        )

        self._populate_menu(items=memu_file_items, menu=menu_file)
        menubar.append(menuitem_file)

        # Edit #
        menu_edit = Gtk.Menu()
        menuitem_edit = Gtk.MenuItem(label='Edit')
        menuitem_edit.set_submenu(menu_edit)

        memu_edit_items = (
            MENUBAR('Preference', self._create_submenu_item, events.run_events_gui, EventType.KB_OPEN_DIALOG_PREFERENCES, None,),
            MENUBAR('Keybindings', self._create_submenu_item, events.run_events_gui, EventType.KB_OPEN_DIALOG_KEYBINDINGS, None,),
        )

        self._populate_menu(items=memu_edit_items, menu=menu_edit)
        menubar.append(menuitem_edit)

        # View #
        menu_view = Gtk.Menu()
        menuitem_view = Gtk.MenuItem(label='View')
        menuitem_view.set_submenu(menu_view)

        memu_edit_items = (
            MENUBAR('Stretch Small Images', self._create_submenu_item, events.run_events_gui, EventType.KB_CHANGE_STRETCH, None),
            MENUBAR('separator', self._create_separator, None, None, None),
            MENUBAR('Best Fit Mode', self._create_submenu_item, events.run_events_gui, EventType.KB_CHANGE_ZOOM_MODE, {'value': ZoomModes.BEST}),
            MENUBAR('Fit Width Mode', self._create_submenu_item, events.run_events_gui, EventType.KB_CHANGE_ZOOM_MODE, {'value': ZoomModes.WIDTH}),
            MENUBAR('Fit Height Mode', self._create_submenu_item, events.run_events_gui, EventType.KB_CHANGE_ZOOM_MODE, {'value': ZoomModes.HEIGHT}),
            MENUBAR('Fit Size Mode', self._create_submenu_item, events.run_events_gui, EventType.KB_CHANGE_ZOOM_MODE, {'value': ZoomModes.SIZE}),
            MENUBAR('Manual Zoom Mode', self._create_submenu_item, events.run_events_gui, EventType.KB_CHANGE_ZOOM_MODE, {'value': ZoomModes.MANUAL}),
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
            MENUBAR('Rotate 90°', self._create_submenu_item, events.run_events_gui, EventType.KB_PAGE_ROTATE, {'rotation': 90}),
            MENUBAR('Rotate 180°', self._create_submenu_item, events.run_events_gui, EventType.KB_PAGE_ROTATE, {'rotation': 180}),
            MENUBAR('Rotate 270°', self._create_submenu_item, events.run_events_gui, EventType.KB_PAGE_ROTATE, {'rotation': 270}),
        )

        self._populate_menu(items=memu_tools_items, menu=menu_tools)
        menubar.append(menuitem_tools)

        # Help #
        menu_help = Gtk.Menu()
        menuitem_help = Gtk.MenuItem(label='Help')
        menuitem_help.set_submenu(menu_help)

        memu_help_items = (
            MENUBAR('About', self._create_submenu_item, events.run_events_gui, EventType.KB_OPEN_DIALOG_ABOUT, None),
        )

        self._populate_menu(items=memu_help_items, menu=menu_help)
        menubar.append(menuitem_help)

        #
        self.show_all()

    def _populate_menu(self, items: tuple, menu):
        for item in items:
            item.create_function(menu, item.label, item.event, item.event_type, item.event_kwargs)

    def _create_submenu_item(self, menu, label: str, event: Callable, event_type: EventType, event_kwargs: dict):
        item = Gtk.MenuItem()
        item.set_label(label)
        item.connect('activate', event, event_type, event_kwargs)
        menu.append(item)

    def _create_separator(self, menu, *args):
        menu.append(Gtk.SeparatorMenuItem())
