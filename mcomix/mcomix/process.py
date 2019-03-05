# -*- coding: utf-8 -*-

"""process.py - Process spawning module."""

import os
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


def find_executable(candidates, workdir=None, is_valid_candidate=None):
    """ Find executable in path.

    Return an absolute path to a valid executable or None.

    <workdir> default to the current working directory if not set.

    <is_valid_candidate> is an optional function that must return True
    if the path passed in argument is a valid candidate (to check for
    version number, symlinks to an unsupported variant, etc...).

    If a candidate has a directory component,
    it will be checked relative to <workdir>.
    On Unix:
    - a valid candidate must have execution right
    """
    if workdir is None:
        workdir = os.getcwd()
    workdir = os.path.abspath(workdir)

    search_path = os.environ['PATH'].split(os.pathsep)

    is_valid_exe = lambda exe: \
        os.path.isfile(exe) and \
        os.access(exe, os.R_OK | os.X_OK)

    if is_valid_candidate is None:
        is_valid = is_valid_exe
    else:
        is_valid = lambda exe: \
            is_valid_exe(exe) and \
            is_valid_candidate(exe)

    for name in candidates:
        # Absolute path?
        if os.path.isabs(name):
            if is_valid(name):
                return name

        # Does candidate have a directory component?
        elif os.path.dirname(name):
            # Yes, check relative to working directory.
            path = os.path.normpath(os.path.join(workdir, name))
            if is_valid(path):
                return path

        # Look in search path.
        else:
            for dir in search_path:
                path = os.path.abspath(os.path.join(dir, name))
                if is_valid(path):
                    return path

    return None
