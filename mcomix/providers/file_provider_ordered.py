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

from mcomix.formats.archive import ArchiveSupported
from mcomix.formats.image import ImageSupported
from mcomix.preferences import config
from mcomix.providers.file_provider_base import FileProviderBase

from mcomix_compiled import FileSortDirection, FileSortType, FileTypes

try:
    from mcomix_compiled import sort_alphanumeric
except ImportError:
    from loguru import logger
    logger.warning("Failed to load compiled sort_alphanumeric() module")
    from mcomix.fallback.sort import sort_alphanumeric

class OrderedFileProvider(FileProviderBase):
    """
    This provider will list all files in the same directory as the one passed to the constructor
    """

    def __init__(self, path: Path):
        """
        Initializes the file listing. If <path> is a file,
        directory will be used as base path. If it is a directory, that
        will be used as base file
        """

        super().__init__()

        self.__base_dir = self._set_directory(path)

    def _set_directory(self, path: Path):
        """
        Sets the base directory
        """

        if path.is_dir():
            return path

        return path.parent

    def list_files(self, mode: int):
        """
        Lists all files in the current directory. Returns a list of absolute paths, already sorted
        """

        match mode:
            case FileTypes.IMAGES:
                should_accept = ImageSupported.is_image_file
            case FileTypes.ARCHIVES:
                should_accept = ArchiveSupported.is_archive_file
            case _:
                raise ValueError

        self.files = [file for file in Path(self.__base_dir).iterdir() if should_accept(file)]
        self._sort_files()

        return self.files

    def _sort_files(self):
        """
        Sorts a list of C{files} depending on the current preferences. The list is sorted in-place
        """

        match config['SORT_BY']:
            case FileSortType.NAME:
                self.files = sort_alphanumeric(self.files)
            case FileSortType.LAST_MODIFIED:
                # Most recently modified file first
                self.files.sort(key=lambda filename: Path.stat(filename).st_mtime * -1)
            case FileSortType.SIZE:
                # Smallest file first
                self.files.sort(key=lambda filename: Path.stat(filename).st_size)

        # Default is ascending.
        if config['SORT_ORDER'] == FileSortDirection.DESCENDING:
            self.files.reverse()
