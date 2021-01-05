# -*- coding: utf-8 -*-

import shutil

from loguru import logger


class GetExecutable:
    def __init__(self, find_executable):
        super().__init__()

        self.__find_executable = shutil.which(find_executable)
        if self.__find_executable is None:
            logger.error(f'failed to find {find_executable} executable')

    def get_executable(self):
        return self.__find_executable
