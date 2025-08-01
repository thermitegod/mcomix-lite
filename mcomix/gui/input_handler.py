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

from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

from gi.repository import Gdk, Gtk

from mcomix.lib.events import Events, EventType
from mcomix.preferences import config
from mcomix.view_state import ViewState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.gui.main_window import MainWindow


class InputHandler:
    def __init__(self, window: MainWindow):
        super().__init__()

        self.__window = window

        self.__events = Events()
        self.__events.add_event(EventType.KB_ESCAPE, self.escape_event)
        self.__events.add_event(EventType.KB_SCROLL_WITH_FLIPPING, self.scroll_with_flipping)

        self.__was_fullscreen = False
        self.__previous_size = (None, None)

        # Dispatch keyboard input handling
        # Some keys require modifiers that are irrelevant to the hotkey. Find out and ignore them.
        self.__all_accels_mask = (Gdk.ModifierType.CONTROL_MASK |
                                  Gdk.ModifierType.SHIFT_MASK |
                                  Gdk.ModifierType.MOD1_MASK)

        self.__keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())

        self.__last_pointer_pos_x = 0
        self.__last_pointer_pos_y = 0

    def resize_event(self, widget, event):
        """
        Handle events from resizing and moving the main window
        """

        size = (event.width, event.height)
        if size != self.__previous_size:
            self.__previous_size = size
            self.__events.run_events(EventType.DRAW_PAGE)

    def window_state_event(self, widget, event):
        is_fullscreen = self.__window.is_fullscreen()
        if self.__was_fullscreen != is_fullscreen:
            # Fullscreen state changed.
            self.__was_fullscreen = is_fullscreen

            self.__previous_size = self.__window.get_size()
            self.__events.run_events(EventType.DRAW_PAGE)

    def key_press_event(self, widget, event, *args):
        """
        Handle key press events on the main window
        """

        code = self.__keymap.translate_keyboard_state(event.hardware_keycode,
                                                      event.get_state(), event.group)

        if code[0]:
            keyval = code.keyval
            consumed_modifiers = code.consumed_modifiers

            # If the resulting key is upper case (i.e. SHIFT + key),
            # convert it to lower case and remove SHIFT from the consumed flags
            # to match how keys are registered (<Shift> + lowercase)
            if event.get_state() & Gdk.ModifierType.SHIFT_MASK and keyval != Gdk.keyval_to_lower(keyval):
                keyval = Gdk.keyval_to_lower(keyval)
                consumed_modifiers &= ~Gdk.ModifierType.SHIFT_MASK

            # 'consumed_modifiers' is the modifier that was necessary to type the key
            self.__window.keybindings.execute((keyval, event.get_state() & ~consumed_modifiers & self.__all_accels_mask))

    def escape_event(self):
        """
        Determines the behavior of the ESC key
        """

        if config['ESCAPE_QUITS']:
            self.__window.terminate_program()
        else:
            self.__window.change_fullscreen()

    def scroll_wheel_event(self, widget, event, *args):
        """
        Handle scroll wheel events on the main layout area. The scroll
        wheel flips pages in best fit mode and scrolls the scrollbars otherwise
        """

        if event.get_state() & Gdk.ModifierType.BUTTON2_MASK:
            return

        deltas = event.get_scroll_deltas()

        if deltas.delta_y < 0:
            # Gdk.ScrollDirection.UP
            if event.get_state() & Gdk.ModifierType.CONTROL_MASK:
                self.__window.manual_zoom_in()
            else:
                self.scroll_with_flipping(0, -config['PIXELS_TO_SCROLL_PER_MOUSE_WHEEL_EVENT'])
        elif deltas.delta_y > 0:
            # Gdk.ScrollDirection.DOWN
            if event.get_state() & Gdk.ModifierType.CONTROL_MASK:
                self.__window.manual_zoom_out()
            else:
                self.scroll_with_flipping(0, config['PIXELS_TO_SCROLL_PER_MOUSE_WHEEL_EVENT'])
        elif not config['FLIP_WITH_WHEEL']:
            return
        elif deltas.delta_x > 0:
            # Gdk.ScrollDirection.RIGHT
            self.__events.run_events(EventType.KB_PAGE_FLIP, {'number_of_pages': -1})
        elif deltas.delta_x < 0:
            # Gdk.ScrollDirection.LEFT
            self.__events.run_events(EventType.KB_PAGE_FLIP, {'number_of_pages': 1})

    def mouse_press_event(self, widget, event):
        """
        Handle mouse click events on the main layout area
        """

        match event.button:
            case 1:
                pass
            case 2:
                pass
            case 3:
                pass
            case 4:
                pass

    def mouse_release_event(self, widget, event):
        """
        Handle mouse button release events on the main layout area
        """

        match event.button:
            case 1:
                pass
            case 2:
                pass
            case 3:
                pass
            case 4:
                pass

    def mouse_move_event(self, widget, event):
        """
        Handle mouse pointer movement events
        """

        if 'GDK_BUTTON1_MASK' in event.get_state().value_names:
            self.__window.cursor_handler.set_cursor_grab()
            self._scroll(self.__last_pointer_pos_x - event.x_root,
                         self.__last_pointer_pos_y - event.y_root)
            self.__last_pointer_pos_x = event.x_root
            self.__last_pointer_pos_y = event.y_root

    def drag_n_drop_event(self, widget, context, x, y, selection, drag_id, eventtime):
        """
        Handle drag-n-drop events on the main layout area
        """

        # The drag source is inside MComix itself, so we ignore.
        if Gtk.drag_get_source_widget(context) is not None:
            return

        uris = selection.get_uris()
        if not uris:
            return

        paths = [Path(url2pathname(urlparse(uri).path)) for uri in uris]
        self.__window.file_handler.open_file_init(paths)

    def scroll_with_flipping(self, x: int, y: int):
        """
        Handle scrolling with the scroll wheel or the arrow keys, for which
        the pages might be flipped depending on the preferences.  Returns True
        if able to scroll without flipping and False if a new page was flipped to
        """

        if not config['FLIP_WITH_WHEEL']:
            return

        if self._scroll(x, y):
            return True

        if y > 0 or (ViewState.is_manga_mode and x < 0) or \
                (not ViewState.is_manga_mode and x > 0):
            self.__events.run_events(EventType.KB_PAGE_FLIP, {'number_of_pages': 1})
        else:
            self.__events.run_events(EventType.KB_PAGE_FLIP, {'number_of_pages': -1})

    def _scroll(self, x: int, y: int):
        """
        Scroll <x> px horizontally and <y> px vertically. If <bound> is
        'first' or 'second', we will not scroll out of the first or second
        page respectively (dependent on manga mode). The <bound> argument
        only makes sense in double page mode.

        :returns: True if call resulted in new adjustment values, False otherwise
        """

        old_hadjust = self.__window.hadjust.get_value()
        old_vadjust = self.__window.vadjust.get_value()

        visible_width, visible_height = self.__window.get_visible_area_size()

        hadjust_upper = max(0, self.__window.hadjust.get_upper() - visible_width)
        vadjust_upper = max(0, self.__window.vadjust.get_upper() - visible_height)
        hadjust_lower = 0

        new_hadjust = old_hadjust + x
        new_vadjust = old_vadjust + y

        new_hadjust = max(hadjust_lower, new_hadjust)
        new_vadjust = max(0, new_vadjust)

        new_hadjust = min(hadjust_upper, new_hadjust)
        new_vadjust = min(vadjust_upper, new_vadjust)

        self.__window.hadjust.set_value(new_hadjust)
        self.__window.vadjust.set_value(new_vadjust)

        return old_vadjust != new_vadjust or old_hadjust != new_hadjust
