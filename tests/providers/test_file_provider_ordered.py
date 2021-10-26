# -*- coding: utf-8 -*-

import pytest
from pathlib import Path

from mcomix.providers.file_provider_ordered import OrderedFileProvider


# TODO
# more tests once libarchive tests are done


def test_ordered_file_provider_base_file():
    assert OrderedFileProvider(Path(__file__)).get_directory() == Path(__file__).parent

def test_ordered_file_provider_base_dir():
    assert OrderedFileProvider(Path(__file__).parent).get_directory() == Path(__file__).parent

