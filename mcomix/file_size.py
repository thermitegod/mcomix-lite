# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.preferences import config


class FileSize:
    def __init__(self, path: Path):
        super().__init__()

        if config['SI_UNITS']:
            unit_size = 1000.0
            unit_symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
        else:
            unit_size = 1024.0
            unit_symbols = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')

        try:
            n = Path.stat(path).st_size

            s = 0
            while n >= unit_size:
                s += 1
                n /= unit_size

            self.__formated_size = f'{n:.3f} {unit_symbols[s]}'
        except (AttributeError, FileNotFoundError):
            logger.warning(f'failed to get file size for: {path}')
            self.__formated_size = 'unknown'

    @property
    def size(self):
        return self.__formated_size
