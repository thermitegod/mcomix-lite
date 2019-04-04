# -*- coding: utf-8 -*-

"""cursor_handler.py - Cursor handler"""

from gi.repository import GLib, Gdk

from mcomix import constants


class CursorHandler(object):
    def __init__(self, window):
        self._window = window
        self._timer_id = None
        self._auto_hide = False
        self._current_cursor = constants.NORMAL_CURSOR

    def set_cursor_type(self, cursor):
        """Set the cursor to type <cursor>. Supported cursor types are
        available as constants in this module. If <cursor> is not one of the
        cursor constants above, it must be a Gdk.Cursor"""
        if cursor == constants.NORMAL_CURSOR:
            mode = None
        elif cursor == constants.GRAB_CURSOR:
            mode = Gdk.Cursor.new(Gdk.CursorType.FLEUR)
        elif cursor == constants.WAIT_CURSOR:
            mode = Gdk.Cursor.new(Gdk.CursorType.WATCH)
        elif cursor == constants.NO_CURSOR:
            mode = self._get_hidden_cursor()
        else:
            mode = cursor

        self._window.set_cursor(mode)

        self._current_cursor = cursor

        if self._auto_hide:
            if cursor == constants.NORMAL_CURSOR:
                self._set_hide_timer()
            else:
                self._kill_timer()

    def auto_hide_on(self):
        """Signal that the cursor should auto-hide from now on (e.g. that we are entering fullscreen)"""
        self._auto_hide = True

        if self._current_cursor == constants.NORMAL_CURSOR:
            self._set_hide_timer()

    def refresh(self):
        """Refresh the current cursor (i.e. display it and set a new timer in
        fullscreen). Used when we move the cursor"""
        if self._auto_hide:
            self.set_cursor_type(self._current_cursor)

    def _on_timeout(self):
        mode = self._get_hidden_cursor()
        self._window.set_cursor(mode)
        self._timer_id = None
        return False

    def _set_hide_timer(self):
        self._kill_timer()
        self._timer_id = GLib.timeout_add(2000, self._on_timeout)

    def _kill_timer(self):
        if self._timer_id is not None:
            GLib.source_remove(self._timer_id)
            self._timer_id = None

    @staticmethod
    def _get_hidden_cursor():
        return Gdk.Cursor.new(Gdk.CursorType.BLANK_CURSOR)
