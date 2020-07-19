# -*- coding: utf-8 -*-

"""process.py - Process spawning module"""

import subprocess

NULL = subprocess.DEVNULL
PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT


def call(args, stdin=NULL, stdout=NULL, stderr=NULL, universal_newlines=False):
    return subprocess.call(args, stdin=stdin, stdout=stdout, stderr=stderr,
                           universal_newlines=universal_newlines, creationflags=0) == 0


def popen(args, stdin=NULL, stdout=PIPE, stderr=NULL, universal_newlines=False):
    return subprocess.Popen(args, stdin=stdin, stdout=stdout, stderr=stderr,
                            universal_newlines=universal_newlines, creationflags=0)
