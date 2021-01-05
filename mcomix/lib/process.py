# -*- coding: utf-8 -*-

import subprocess


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
