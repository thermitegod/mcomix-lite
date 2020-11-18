# -*- coding: utf-8 -*-

from mcomix.preferences import config


class _Utils:
    def __init__(self):
        super().__init__()

        if config['SI_UNITS']:
            self.__unit_size = 1000
            self.__unit_symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
        else:
            self.__unit_size = 1024
            self.__unit_symbols = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')

    def format_byte_size(self, n: int):
        s = 0
        while n >= self.__unit_size:
            s += 1
            n /= float(self.__unit_size)

        return f'{n:.3f} {self.__unit_symbols[s]}'


Utils = _Utils()
