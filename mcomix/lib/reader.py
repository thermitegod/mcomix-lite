# -*- coding: utf-8 -*-

import io
from pathlib import Path
from threading import Lock

_IOLock = Lock()


class LockedFileIO(io.BytesIO):
    def __init__(self, path: Path = None):
        super().__init__()

        with _IOLock:
            with Path.open(path, 'rb') as f:
                super().__init__(f.read())
