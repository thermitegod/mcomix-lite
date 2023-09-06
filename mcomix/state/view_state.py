# -*- coding: utf-8 -*-

from mcomix.preferences import config


class _ViewState:
    def __init__(self):
        super().__init__()

        self.__is_manga_mode: bool = config['DEFAULT_MANGA_MODE']
        self.__is_displaying_double: bool = False

    @property
    def is_manga_mode(self) -> bool:
        return self.__is_manga_mode

    @is_manga_mode.setter
    def is_manga_mode(self, value: bool) -> None:
        self.__is_manga_mode = value

    @property
    def is_displaying_double(self) -> bool:
        return self.__is_displaying_double

    @is_displaying_double.setter
    def is_displaying_double(self, value: bool) -> None:
        self.__is_displaying_double = value


ViewState = _ViewState()
