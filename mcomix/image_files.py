# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path


class ImageFiles():
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
