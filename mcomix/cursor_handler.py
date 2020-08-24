# -*- coding: utf-8 -*-

"""cursor_handler.py - Cursor handler"""

from gi.repository import GLib, Gdk

from mcomix import constants


class CursorHandler:
    def __init__(self, window):
        self.__window = window
        self.__timer_id = None
        self.__auto_hide = False
        self.__current_cursor = constants.CURSOR_NORMAL

    def set_cursor_type(self, cursor):
        """
        Set the cursor to type <cursor>. Supported cursor types are
        available as constants in this module. If <cursor> is not one of the
        cursor constants above, it must be a Gdk.Cursor
        """

        if cursor == constants.CURSOR_NORMAL:
            mode = None
        elif cursor == constants.CURSOR_GRAB:
            mode = Gdk.Cursor.new(Gdk.CursorType.FLEUR)
        elif cursor == constants.CURSOR_WAIT:
            mode = Gdk.Cursor.new(Gdk.CursorType.WATCH)
        elif cursor == constants.CURSOR_NONE:
            mode = self._get_hidden_cursor()
        else:
            mode = cursor

        self.__window.set_cursor(mode)

        self.__current_cursor = cursor

        if self.__auto_hide:
            if cursor == constants.CURSOR_NORMAL:
                self._set_hide_timer()
            else:
                self._kill_timer()

    def auto_hide_on(self):
        """
        Signal that the cursor should auto-hide from now on (e.g. that we are entering fullscreen)
        """

        self.__auto_hide = True
        if self.__current_cursor == constants.CURSOR_NORMAL:
            self._set_hide_timer()

    def refresh(self):
        """
        Refresh the current cursor (i.e. display it and set a new timer in
        fullscreen). Used when we move the cursor
        """

        if self.__auto_hide:
            self.set_cursor_type(self.__current_cursor)

    def _on_timeout(self):
        mode = self._get_hidden_cursor()
        self.__window.set_cursor(mode)
        self.__timer_id = None
        return False

    def _set_hide_timer(self):
        self._kill_timer()
        self.__timer_id = GLib.timeout_add(2000, self._on_timeout)

    def _kill_timer(self):
        if self.__timer_id is not None:
            GLib.source_remove(self.__timer_id)
            self.__timer_id = None

    @staticmethod
    def _get_hidden_cursor():
        return Gdk.Cursor.new(Gdk.CursorType.BLANK_CURSOR)
