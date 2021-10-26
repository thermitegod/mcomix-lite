# -*- coding: utf-8 -*-

from mcomix.enums.file_sort import FileSortType, FileSortDirection


def test_file_sort_none():
    assert FileSortType.NONE.value == 0

def test_file_sort_name():
    assert FileSortType.NAME.value == 1

def test_file_sort_size():
    assert FileSortType.SIZE.value == 2

def test_file_sort_last_mod():
    assert FileSortType.LAST_MODIFIED.value == 3

def test_file_sort_literal():
    assert FileSortType.NAME_LITERAL.value == 4

def test_file_sort_descending():
    assert FileSortDirection.DESCENDING.value == 0

def test_file_sort_ascending():
    assert FileSortDirection.ASCENDING.value == 1
