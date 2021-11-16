# -*- coding: utf-8 -*-


class FileProviderBase:
    __slots__ = ('files',)

    def __init__(self):
        super().__init__()

        self.files = []

    def list_files(self, mode: int):
        raise NotImplementedError
