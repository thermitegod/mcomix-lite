# -*- coding: utf-8 -*-

"""event_handler.py - Event handling (keyboard, mouse, etc.) for the main window"""

from gi.repository import Gdk, Gtk

from mcomix.constants import Constants
from mcomix.preferences import config


class EventHandler:
    def __init__(self, window, keybindings):
        super().__init__()

        self.__window = window
        self.__keybindings = keybindings

        self.__last_pointer_pos_x = 0
        self.__last_pointer_pos_y = 0

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
            toggleaction = self.__window.actiongroup.get_action('fullscreen')
            toggleaction.set_sensitive(True)
            if is_fullscreen:
                redraw = True
            else:
                # Only redraw if we don't need to restore geometry.
                redraw = not self.__window.restore_window_geometry()
            self.__window.update_toggles_sensitivity()
            if redraw:
                self.__window.previous_size = self.__window.get_size()
                self.__window.draw_image()

    def register_key_events(self):
        """
        Registers keyboard events and their default binings, and hooks
        them up with their respective callback functions
        """

        # Navigation keys
        self.__keybindings.register('previous_page',
                                    self.__window.flip_page, kwargs={'number_of_pages': -1})
        self.__keybindings.register('next_page',
                                    self.__window.flip_page, kwargs={'number_of_pages': +1})
        self.__keybindings.register('previous_page_singlestep',
                                    self.__window.flip_page, kwargs={'number_of_pages': -1, 'single_step': True})
        self.__keybindings.register('next_page_singlestep',
                                    self.__window.flip_page, kwargs={'number_of_pages': +1, 'single_step': True})
        self.__keybindings.register('previous_page_ff',
                                    self.__window.flip_page, kwargs={'number_of_pages': -10})
        self.__keybindings.register('next_page_ff',
                                    self.__window.flip_page, kwargs={'number_of_pages': +10})
        self.__keybindings.register('first_page',
                                    self.__window.first_page)
        self.__keybindings.register('last_page',
                                    self.__window.last_page)
        self.__keybindings.register('go_to',
                                    self.__window.page_select)

        # Enter/exit fullscreen.
        self.__keybindings.register('exit_fullscreen',
                                    self.escape_event)

        # View modes
        self.__keybindings.register('double_page',
                                    self.__window.actiongroup.get_action('double_page').activate)
        self.__keybindings.register('best_fit_mode',
                                    self.__window.actiongroup.get_action('best_fit_mode').activate)
        self.__keybindings.register('fit_width_mode',
                                    self.__window.actiongroup.get_action('fit_width_mode').activate)
        self.__keybindings.register('fit_height_mode',
                                    self.__window.actiongroup.get_action('fit_height_mode').activate)
        self.__keybindings.register('fit_size_mode',
                                    self.__window.actiongroup.get_action('fit_size_mode').activate)
        self.__keybindings.register('fit_manual_mode',
                                    self.__window.actiongroup.get_action('fit_manual_mode').activate)
        self.__keybindings.register('manga_mode',
                                    self.__window.actiongroup.get_action('manga_mode').activate)
        self.__keybindings.register('keep_transformation',
                                    self.__window.actiongroup.get_action('keep_transformation').activate)
        self.__keybindings.register('lens',
                                    self.__window.actiongroup.get_action('lens').activate)
        self.__keybindings.register('stretch',
                                    self.__window.actiongroup.get_action('stretch').activate)

        # Zooming commands for manual zoom mode
        self.__keybindings.register('zoom_in',
                                    self.__window.actiongroup.get_action('zoom_in').activate)
        self.__keybindings.register('zoom_out',
                                    self.__window.actiongroup.get_action('zoom_out').activate)

        # Zoom out is already defined as GTK menu hotkey
        self.__keybindings.register('zoom_original',
                                    self.__window.actiongroup.get_action('zoom_original').activate)
        self.__keybindings.register('rotate_90',
                                    self.__window.rotate_x,
                                    kwargs={'rotation': 90})
        self.__keybindings.register('rotate_270',
                                    self.__window.rotate_x,
                                    kwargs={'rotation': 270})
        self.__keybindings.register('rotate_180',
                                    self.__window.rotate_x,
                                    kwargs={'rotation': 180})
        self.__keybindings.register('flip_horiz',
                                    self.__window.flip_horizontally)
        self.__keybindings.register('flip_vert',
                                    self.__window.flip_vertically)
        self.__keybindings.register('no_autorotation',
                                    self.__window.actiongroup.get_action('no_autorotation').activate)
        self.__keybindings.register('rotate_90_width',
                                    self.__window.actiongroup.get_action('rotate_90_width').activate)
        self.__keybindings.register('rotate_270_width',
                                    self.__window.actiongroup.get_action('rotate_270_width').activate)
        self.__keybindings.register('rotate_90_height',
                                    self.__window.actiongroup.get_action('rotate_90_height').activate)
        self.__keybindings.register('rotate_270_height',
                                    self.__window.actiongroup.get_action('rotate_270_height').activate)

        # Arrow keys scroll the image
        self.__keybindings.register('scroll_down',
                                    self._scroll_with_flipping,
                                    kwargs={'x': 0, 'y': config['PIXELS_TO_SCROLL_PER_KEY_EVENT']})
        self.__keybindings.register('scroll_up',
                                    self._scroll_with_flipping,
                                    kwargs={'x': 0, 'y': -config['PIXELS_TO_SCROLL_PER_KEY_EVENT']})
        self.__keybindings.register('scroll_right',
                                    self._scroll_with_flipping,
                                    kwargs={'x': config['PIXELS_TO_SCROLL_PER_KEY_EVENT'], 'y': 0})
        self.__keybindings.register('scroll_left',
                                    self._scroll_with_flipping,
                                    kwargs={'x': -config['PIXELS_TO_SCROLL_PER_KEY_EVENT'], 'y': 0})

        # File operations
        self.__keybindings.register('close',
                                    self.__window.filehandler.close_file)
        self.__keybindings.register('quit',
                                    self.__window.terminate_program)
        self.__keybindings.register('delete',
                                    self.__window.move_file, kwargs={'move_else_delete': False})
        self.__keybindings.register('move_file',
                                    self.__window.move_file, kwargs={'move_else_delete': True})
        self.__keybindings.register('extract_page',
                                    self.__window.extract_page)
        self.__keybindings.register('refresh_archive',
                                    self.__window.filehandler.refresh_file)
        self.__keybindings.register('next_archive',
                                    self.__window.filehandler.open_archive_direction, kwargs={'forward': True})
        self.__keybindings.register('previous_archive',
                                    self.__window.filehandler.open_archive_direction, kwargs={'forward': False})
        self.__keybindings.register('properties',
                                    self.__window.actiongroup.get_action('properties').activate)
        self.__keybindings.register('preferences',
                                    self.__window.actiongroup.get_action('preferences').activate)
        self.__keybindings.register('enhance_image',
                                    self.__window.actiongroup.get_action('enhance_image').activate)

        # User interface
        self.__keybindings.register('minimize',
                                    self.__window.minimize)
        self.__keybindings.register('fullscreen',
                                    self.__window.actiongroup.get_action('fullscreen').activate)
        self.__keybindings.register('menubar',
                                    self.__window.actiongroup.get_action('menubar').activate)
        self.__keybindings.register('statusbar',
                                    self.__window.actiongroup.get_action('statusbar').activate)
        self.__keybindings.register('scrollbar',
                                    self.__window.actiongroup.get_action('scrollbar').activate)
        self.__keybindings.register('thumbnails',
                                    self.__window.actiongroup.get_action('thumbnails').activate)
        self.__keybindings.register('hide_all',
                                    self.__window.actiongroup.get_action('hide_all').activate)

    def key_press_event(self, widget, event, *args):
        """
        Handle key press events on the main window
        """

        # Dispatch keyboard input handling
        # Some keys require modifiers that are irrelevant to the hotkey. Find out and ignore them.
        ALL_ACCELS_MASK = (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK | Gdk.ModifierType.MOD1_MASK)

        keymap = Gdk.Keymap.get_default()

        code = keymap.translate_keyboard_state(event.hardware_keycode, event.get_state(), event.group)
        if code[0]:
            keyval = code[1]
            consumed = code[4]

            # If the resulting key is upper case (i.e. SHIFT + key),
            # convert it to lower case and remove SHIFT from the consumed flags
            # to match how keys are registered (<Shift> + lowercase)
            if event.get_state() & Gdk.ModifierType.SHIFT_MASK and keyval != Gdk.keyval_to_lower(keyval):
                keyval = Gdk.keyval_to_lower(keyval)
                consumed &= ~Gdk.ModifierType.SHIFT_MASK

            # 'consumed' is the modifier that was necessary to type the key
            self.__keybindings.execute((keyval, event.get_state() & ~consumed & ALL_ACCELS_MASK))

    def escape_event(self):
        """
        Determines the behavior of the ESC key
        """

        if config['ESCAPE_QUITS']:
            self.__window.terminate_program()
        else:
            self.__window.actiongroup.get_action('fullscreen').set_active(False)

    def scroll_wheel_event(self, widget, event, *args):
        """
        Handle scroll wheel events on the main layout area. The scroll
        wheel flips pages in best fit mode and scrolls the scrollbars otherwise
        """

        if not config['FLIP_WITH_WHEEL']:
            return

        if event.get_state() & Gdk.ModifierType.BUTTON2_MASK:
            return

        has_delta, delta_x, delta_y = event.get_scroll_deltas()

        if delta_y < 0:
            # Gdk.ScrollDirection.UP
            if event.get_state() & Gdk.ModifierType.CONTROL_MASK:
                self.__window.manual_zoom_in()
            else:
                self._scroll_with_flipping(0, -config['PIXELS_TO_SCROLL_PER_MOUSE_WHEEL_EVENT'])
        elif delta_y > 0:
            # Gdk.ScrollDirection.DOWN
            if event.get_state() & Gdk.ModifierType.CONTROL_MASK:
                self.__window.manual_zoom_out()
            else:
                self._scroll_with_flipping(0, config['PIXELS_TO_SCROLL_PER_MOUSE_WHEEL_EVENT'])
        elif delta_x > 0:
            # Gdk.ScrollDirection.RIGHT
            if self.get_manga_flip_direction():
                self.__window.flip_page(number_of_pages=-1)
            else:
                self.__window.flip_page(number_of_pages=+1)
        elif delta_x < 0:
            # Gdk.ScrollDirection.LEFT
            if self.get_manga_flip_direction():
                self.__window.flip_page(number_of_pages=+1)
            else:
                self.__window.flip_page(number_of_pages=-1)

    def mouse_press_event(self, widget, event):
        """
        Handle mouse click events on the main layout area
        """

        if event.button == 1:
            pass

        elif event.button == 2:
            self.__window.actiongroup.get_action('lens').set_active(True)

        elif event.button == 3:
            pass

        elif event.button == 4:
            pass

    def mouse_release_event(self, widget, event):
        """
        Handle mouse button release events on the main layout area
        """

        self.__window.cursor_handler.set_cursor_type(Constants.CURSOR['NORMAL'])

        if event.button == 1:
            pass

        elif event.button == 2:
            self.__window.actiongroup.get_action('lens').set_active(False)

        elif event.button == 3:
            pass

        elif event.button == 4:
            pass

    def mouse_move_event(self, widget, event):
        """
        Handle mouse pointer movement events
        """

        if 'GDK_BUTTON1_MASK' in event.get_state().value_names:
            self.__window.cursor_handler.set_cursor_type(Constants.CURSOR['GRAB'])
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

        paths = [uri.removeprefix('file://') for uri in uris]
        self.__window.filehandler.open_file(paths)

    def _scroll_with_flipping(self, x: int, y: int):
        """
        Handle scrolling with the scroll wheel or the arrow keys, for which
        the pages might be flipped depending on the preferences.  Returns True
        if able to scroll without flipping and False if a new page was flipped to
        """

        if self.__window.scroll(x, y):
            return True

        if y > 0 or (self.get_manga_flip_direction() and x < 0) or \
                (not self.get_manga_flip_direction() and x > 0):
            self.__window.flip_page(number_of_pages=+1)
        else:
            self.__window.flip_page(number_of_pages=-1)
