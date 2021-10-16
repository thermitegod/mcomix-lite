# -*- coding: utf-8 -*-

"""event_handler.py - Event handling (keyboard, mouse, etc.) for the main window"""

from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

from gi.repository import Gdk, Gtk

from mcomix.preferences import config


class EventHandler:
    def __init__(self, window):
        super().__init__()

        self.__window = window
        self.__keybindings = None
        self.__keybindings_map = None

        # Dispatch keyboard input handling
        # Some keys require modifiers that are irrelevant to the hotkey. Find out and ignore them.
        self.__all_accels_mask = (Gdk.ModifierType.CONTROL_MASK |
                                  Gdk.ModifierType.SHIFT_MASK |
                                  Gdk.ModifierType.MOD1_MASK)

        self.__keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())

        self.__last_pointer_pos_x = 0
        self.__last_pointer_pos_y = 0

    def event_handler_init(self):
        """
        lazy init to avoid circular deps
        """

        self.__keybindings = self.__window.keybindings
        self.__keybindings_map = self.__window.keybindings_map

    def get_manga_flip_direction(self):
        if (self.__window.is_manga_mode and not config['MANGA_FLIP_RIGHT']) or \
                (not self.__window.is_manga_mode and config['WESTERN_FLIP_LEFT']):
            return True
        return False

    def resize_event(self, widget, event):
        """
        Handle events from resizing and moving the main window
        """

        size = (event.width, event.height)
        if size != self.__window.previous_size:
            self.__window.previous_size = size
            self.__window.draw_image()

    def window_state_event(self, widget, event):
        is_fullscreen = self.__window.is_fullscreen()
        if self.__window.was_fullscreen != is_fullscreen:
            # Fullscreen state changed.
            self.__window.was_fullscreen = is_fullscreen
            # Re-enable control, now that transition is complete.
            if is_fullscreen:
                redraw = True
            else:
                # Only redraw if we don't need to restore geometry.
                redraw = not self.__window.restore_window_geometry()
            if redraw:
                self.__window.previous_size = self.__window.get_size()
                self.__window.draw_image()

    def register_key_events(self):
        """
        Registers keyboard events and their default binings, and hooks
        them up with their respective callback functions
        """

        for action in self.__keybindings_map.keys():
            self.__keybindings.register(
                name=action,
                callback=self.__keybindings_map[action].key_event.callback,
                callback_kwargs=self.__keybindings_map[action].key_event.callback_kwargs,
            )

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
            self.__keybindings.execute((keyval, event.get_state() & ~consumed_modifiers & self.__all_accels_mask))

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
            if self.get_manga_flip_direction():
                self.__window.flip_page(number_of_pages=-1)
            else:
                self.__window.flip_page(number_of_pages=+1)
        elif deltas.delta_x < 0:
            # Gdk.ScrollDirection.LEFT
            if self.get_manga_flip_direction():
                self.__window.flip_page(number_of_pages=+1)
            else:
                self.__window.flip_page(number_of_pages=-1)

    def mouse_press_event(self, widget, event):
        """
        Handle mouse click events on the main layout area
        """

        match event.button:
            case 1:
                pass
            case 2:
                self.__window.lens.toggle(True)
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
                self.__window.lens.toggle(False)
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
            self.__window.scroll(self.__last_pointer_pos_x - event.x_root,
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

        self.__window.filehandler.initialize_fileprovider(path=paths)
        self.__window.filehandler.open_file(paths[0])

    def scroll_with_flipping(self, x: int, y: int):
        """
        Handle scrolling with the scroll wheel or the arrow keys, for which
        the pages might be flipped depending on the preferences.  Returns True
        if able to scroll without flipping and False if a new page was flipped to
        """

        if not config['FLIP_WITH_WHEEL']:
            return

        if self.__window.scroll(x, y):
            return True

        if y > 0 or (self.get_manga_flip_direction() and x < 0) or \
                (not self.get_manga_flip_direction() and x > 0):
            self.__window.flip_page(number_of_pages=+1)
        else:
            self.__window.flip_page(number_of_pages=-1)
