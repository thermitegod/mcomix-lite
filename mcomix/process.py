# -*- coding: utf-8 -*-

"""process.py - Process spawning module"""

import shutil
import subprocess
from threading import Thread

NULL = subprocess.DEVNULL
PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT


def call(args, stdin=NULL, stdout=NULL, stderr=NULL, universal_newlines=False):
    return 0 == subprocess.call(args, stdin=stdin, stdout=stdout,
                                universal_newlines=universal_newlines, creationflags=0)


def popen(args, stdin=NULL, stdout=PIPE, stderr=NULL, universal_newlines=False):
    return subprocess.Popen(args, stdin=stdin, stdout=stdout, stderr=stderr,
                            universal_newlines=universal_newlines, creationflags=0)


def call_thread(args):
    # call command in thread, so drop std* and set no buffer
    params = dict(stdin=NULL, stdout=NULL, stderr=NULL, bufsize=0, creationflags=0)
    thread = Thread(target=subprocess.call, args=(args,), kwargs=params, daemon=True)
    thread.start()


def find_executable(executable):
    """Find executable in path"""
    exe = None
    try:
        exe = shutil.which(executable)
    except NameError:
        pass
    return exe
