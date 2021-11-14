# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class MenubarShim:
    """
    Shim for MainWindow, prevents needing *args in methods used by the GUI
    """

    __slots__ = ('__window',)

    def __init__(self, window: MainWindow):
        super().__init__()

        self.__window = window

    def rotate_x(self, menubar, rotation: int):
        self.__window.rotate_x(rotation)

    def change_zoom_mode(self, menubar, value: int = None):
        self.__window.change_zoom_mode(value)

    def open_dialog(self, menubar, dialog):
        self.__window.open_dialog(dialog)

    def extract_page(self, menubar):
        self.__window.extract_page()

    def move_file(self, menubar):
        self.__window.move_file()

    def trash_file(self, menubar):
        self.__window.trash_file()

    def minimize(self, menubar):
        self.__window.minimize()

    def terminate_program(self, menubar):
        self.__window.terminate_program()

    def change_stretch(self, menubar):
        self.__window.change_stretch()

    def refresh_file(self, menubar):
        self.__window.refresh_file()

    def close_file(self, menubar):
        self.__window.close_file()
