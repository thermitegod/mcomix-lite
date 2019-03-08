# -*- coding: utf-8 -*-

"""process.py - Process spawning module."""

import subprocess
import sys
from threading import Thread

NULL = subprocess.DEVNULL
PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT


# Convert argument vector to system's file encoding where necessary
# to prevent automatic conversion when appending Unicode strings
# to byte strings later on.
def _fix_args(args):
    fixed_args = []
    for arg in args:
        if isinstance(arg, str):
            fixed_args.append(arg.encode(sys.getfilesystemencoding()))
        else:
            fixed_args.append(arg)
    return fixed_args


def call(args, stdin=NULL, stdout=NULL, stderr=NULL, universal_newlines=False):
    return 0 == subprocess.call(_fix_args(args), stdin=stdin,
                                stdout=stdout,
                                universal_newlines=universal_newlines,
                                creationflags=0)


def popen(args, stdin=NULL, stdout=PIPE, stderr=NULL, universal_newlines=False):
    return subprocess.Popen(_fix_args(args), stdin=stdin,
                            stdout=stdout, stderr=stderr,
                            universal_newlines=universal_newlines,
                            creationflags=0)


def call_thread(args):
    # call command in thread, so drop std* and set no buffer
    params = dict(
            stdin=NULL, stdout=NULL, stderr=NULL,
            bufsize=0, creationflags=0
    )
    thread = Thread(target=subprocess.call,
                    args=(args,), kwargs=params, daemon=True)
    thread.start()
