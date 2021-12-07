# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.lib.metaclass import SingleInstanceMetaClass


class SingleClass(metaclass=SingleInstanceMetaClass):
    def __init__(self):
        self.a: int = 1

class SingleClassArg(metaclass=SingleInstanceMetaClass):
    def __init__(self, value: int):
        self.a: int = value


def test_single_instance_class():
    test_class_01 = SingleClass()
    test_class_02 = SingleClass()

    assert test_class_01 is test_class_02


def test_single_instance_class_attr():
    test_class_01 = SingleClass()
    test_class_02 = SingleClass()

    test_class_01.a = 5
    test_class_02.a = 2

    assert test_class_01.a == test_class_02.a


def test_single_instance_arg_class():
    test_class_01 = SingleClassArg(5)
    test_class_02 = SingleClassArg(None)

    assert test_class_01 is test_class_02


def test_single_instance_arg_class_attr():
    test_class_01 = SingleClassArg(5)
    test_class_02 = SingleClassArg(None)

    test_class_02.a = 6

    assert test_class_01.a == test_class_02.a
