# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.enums.config_files import ConfigFiles, ConfigPaths


def test_config_files__is_pathlike():
    for f in ConfigFiles:
        assert isinstance(f.value, Path)

def test_config_paths__is_pathlike():
    for f in ConfigPaths:
        assert isinstance(f.value, Path)
