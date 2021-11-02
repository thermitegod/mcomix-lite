# -*- coding: utf-8 -*-

import io
from threading import Lock

_IOLock = Lock()


class LockedFileIO(io.BytesIO):
    __slots__ = ()

    def __init__(self, path):
        super().__init__()

        with _IOLock:
            with open(path, mode='rb') as f:
                super().__init__(f.read())
