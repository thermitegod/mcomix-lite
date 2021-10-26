# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.file_size import _FileSize
from mcomix.preferences import config

FileSize = _FileSize()


def test_file_size():
    config['SI_UNITS'] = False
    test_file = Path() / Path(__file__).parent.parent / 'COPYING'
    FileSize = _FileSize()
    assert FileSize(test_file) == '17.814 KiB'

def test_file_size_si():
    config['SI_UNITS'] = True
    test_file = Path() / Path(__file__).parent.parent / 'COPYING'
    FileSize = _FileSize()
    assert FileSize(test_file) == '18.242 KB'

