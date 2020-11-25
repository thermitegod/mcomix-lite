# -*- coding: utf-8 -*-

import shutil
import subprocess

from loguru import logger


class _Process:
    NULL = subprocess.DEVNULL
    PIPE = subprocess.PIPE
    STDOUT = subprocess.STDOUT

    def __init__(self):
        super().__init__()

    @staticmethod
    def call(args, stdin=NULL, stdout=NULL, stderr=NULL, universal_newlines=False):
        return subprocess.call(args, stdin=stdin, stdout=stdout, stderr=stderr,
                               universal_newlines=universal_newlines, creationflags=0) == 0

    @staticmethod
    def popen(args, stdin=NULL, stdout=PIPE, stderr=NULL, universal_newlines=False):
        return subprocess.Popen(args, stdin=stdin, stdout=stdout, stderr=stderr,
                                universal_newlines=universal_newlines, creationflags=0)


Process = _Process()


class GetExecutable:
    def __init__(self, find_executable):
        super().__init__()

        self.__find_executable = shutil.which(find_executable)
        if self.__find_executable is None:
            logger.error(f'failed to find {find_executable} executable')

    def get_executable(self):
        return self.__find_executable
