# -*- coding: utf-8 -*-

import shutil

from loguru import logger


class _GetExecutable:
    def __init__(self):
        super().__init__()

        self.__executables = {
            'SZIP':
                {
                    'BINARY': '7za',
                    'PATH': None,
                    'FOUND': False
                },
            'UNRAR':
                {
                    'BINARY': 'unrar',
                    'PATH': None,
                    'FOUND': False
                },
        }

        for idx, item in enumerate(self.__executables):
            self.__executables[item]['PATH'] = shutil.which(self.__executables[item]['BINARY'])
            self.__executables[item]['FOUND'] = bool(self.__executables[item]['PATH'])
            if self.__executables[item]['PATH'] is None:
                logger.warning(f'failed to find executable for \'{self.__executables[item]}\'')

    @property
    def executables(self):
        return self.__executables


GetExecutable = _GetExecutable()
