# -*- coding: utf-8 -*-

"""cursor_handler.py - Cursor handler"""

from enum import Enum, auto

from gi.repository import GLib, Gdk


class CursorModes(Enum):
    NORMAL = auto()
    GRAB = auto()
    HIDDEN = auto()


class CursorHandler:
    __slots__ = ('__window', '__timer_id', '__auto_hide', '__current_cursor')

    def __init__(self, window):
        super().__init__()

        self.__window = window
        self.__timer_id = None
        self.__auto_hide = False
        self.__current_cursor = CursorModes.NORMAL

    def _set_cursor(self, mode):
        """
        Set the cursor on the main layout area to <mode>.
        """

        self.__window.main_layout.get_window().set_cursor(mode)

    def set_cursor_normal(self):
        self._set_cursor(None)
        self.__current_cursor = CursorModes.NORMAL

        if self.__auto_hide:
            self._set_hide_timer()

    def set_cursor_grab(self):
        self._set_cursor(Gdk.Cursor.new_for_display(Gdk.Display.get_default(), Gdk.CursorType.FLEUR))
        self.__current_cursor = CursorModes.GRAB

        if self.__auto_hide:
            self._kill_timer()

    def set_cursor_hidden(self):
        self._set_cursor(Gdk.Cursor.new_for_display(Gdk.Display.get_default(), Gdk.CursorType.BLANK_CURSOR))
        self.__current_cursor = CursorModes.HIDDEN

        if self.__auto_hide:
            self._kill_timer()

    def auto_hide_on(self):
        """
        Signal that the cursor should auto-hide from now on (e.g. that we are entering fullscreen)
        """

        self.__auto_hide = True
        if self.__current_cursor == CursorModes.NORMAL:
            self._set_hide_timer()

    def auto_hide_off(self):
        """
        Signal that the cursor should *not* auto-hide from now on
        """

        self.__auto_hide = False
        self._kill_timer()

        if self.__current_cursor != CursorModes.NORMAL:
            self.set_cursor_normal()

    def refresh(self, *args):
        """
        Refresh the current cursor (i.e. display it and set a new timer in
        fullscreen). Used when we move the cursor
        """

        if self.__auto_hide:
            self.set_cursor_normal()

    def _on_timeout(self):
        self.set_cursor_hidden()
        self.__timer_id = None
        return False

    def _set_hide_timer(self):
        self._kill_timer()
        self.__timer_id = GLib.timeout_add(2000, self._on_timeout)

    def _kill_timer(self):
        if self.__timer_id is not None:
            GLib.source_remove(self.__timer_id)
            self.__timer_id = None
