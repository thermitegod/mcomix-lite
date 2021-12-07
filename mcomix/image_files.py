# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.lib.metaclass import SingleInstanceMetaClass


class ImageFiles(metaclass=SingleInstanceMetaClass):
    __slots__ = ('__pages', '__paths', '__total_pages')

    def __init__(self) -> None:
        self.__pages = {}
        self.__paths = {}
        self.__total_pages = 0

    def set_image_files(self, image_files: list) -> None:
        for idx, image in enumerate(image_files):
            self.__paths.update({image: idx + 1})
            self.__pages.update({idx + 1: image})

        self.__total_pages = len(self.__pages)

    def get_total_pages(self) -> int:
        return self.__total_pages

    def get_path_from_page(self, page: int) -> Path:
        return self.__pages[page]

    def get_page_from_path(self, path: Path) -> int:
        return self.__paths[path]

    def cleanup(self) -> None:
        self.__pages.clear()
        self.__paths.clear()
        self.__total_pages = 0
