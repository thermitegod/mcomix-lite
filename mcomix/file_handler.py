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

from __future__ import annotations

from pathlib import Path

from loguru import logger

from mcomix.archive_extractor import Extractor
from mcomix.enums import FileSortDirection, FileSortType, FileTypes
from mcomix.formats.archive import ArchiveSupported
from mcomix.file_provider import GetFileProvider
from mcomix.image_files import ImageFiles
from mcomix.image_handler import ImageHandler
from mcomix.lib.events import Events, EventType
from mcomix.lib.metaclass import SingleInstanceMetaClass
from mcomix.preferences import config
from mcomix.sort.sort_alphanumeric import SortAlphanumeric

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class FileHandler(metaclass=SingleInstanceMetaClass):
    """
    The FileHandler keeps track of the actual files/archives opened.
    While ImageHandler takes care of pages/images, this class provides
    the raw file names for archive members and image files, extracts
    archives, and lists directories for image files
    """

    def __init__(self, window: MainWindow):
        super().__init__()

        self.__events = Events()
        self.__events.add_event(EventType.FILE_EXTRACTED, self._extracted_file)
        self.__events.add_event(EventType.FILE_LISTED, self._file_listed)
        self.__events.add_event(EventType.KB_FILE_CLOSE, self.close_file)
        self.__events.add_event(EventType.KB_FILE_REFRESH, self.refresh_file)
        self.__events.add_event(EventType.KB_OPEN_ARCHIVE_DIRECTION, self.open_archive_direction)

        self.__image_handler = ImageHandler()
        self.__image_files = ImageFiles()

        #: Indicates if files/archives are currently loaded/loading.
        self.__file_loaded = False
        self.__file_loading = False
        #: False if current file is not an archive, or unrecognized format.
        self.__is_archive = False

        #: Either path to the current archive, or first file in image list.
        #: This is B{not} the path to the currently open page.
        self.__current_file = None
        #: Reference to L{MainWindow}.
        self.__window = window
        #: Path to opened archive file, or directory containing current images.
        self.__base_path = None
        #: Archive extractor.
        self.__extractor = None
        #: Provides a list of available files/archives in the open directory.
        self.__file_provider_chooser = GetFileProvider()
        self.__file_provider = None

        self.__start_page = 1

        self.__open_first_page = None

        self.update_opening_behavior()

    def update_opening_behavior(self):
        self.__open_first_page = 1 if config['OPEN_FIRST_PAGE'] else -1

    def refresh_file(self):
        """
        Closes the current file(s)/archive and reloads them
        """

        if not self.__file_loaded:
            return

        current_file = self.get_real_path()
        if self.__is_archive:
            start_page = self.__image_handler.get_current_page()
        else:
            start_page = 1
        self.open_file(current_file, start_page)

    def open_file_init(self, paths: list, start_page: int = 1):
        """
        Open the first file pointed to in <paths>,
        and initialize the file provider.
        """

        if not paths:
            return

        self._initialize_fileprovider(paths=paths)
        self.open_file(paths[0], start_page)

    def open_file(self, path: Path, start_page: int = 1):
        """
        Open the file pointed to by <path>.
        If <start_page> is not set we set the current
        page to 1 (first page), if it is set we set the current page to the
        value of <start_page>. If <start_page> is non-positive it means the
        last image.
        """

        self._close()

        self.__is_archive = ArchiveSupported.is_archive_file(path)
        self.__start_page = start_page
        self.__current_file = path

        # Actually open the file(s)/archive passed in path.
        if self.__is_archive:
            self.__base_path = path
            self._open_archive(self.__current_file)
            self.__file_loading = True
        else:
            image_files = self.__file_provider.list_files(mode=FileTypes.IMAGES)
            if self.__current_file.is_dir():
                self.__base_path = self.__current_file
            else:
                self.__base_path = self.__current_file.parent
            self._archive_opened(image_files)

    def _archive_opened(self, image_files: list):
        """
        Called once the archive has been opened and its contents listed
        """

        self.__image_files.set_image_files(image_files)
        self.file_opened()

        if not image_files:
            logger.error(f'No images in "{self.__current_file.name}"')
            return

        if self.__is_archive:
            self.__extractor.extract()

            start_page = self.__start_page
        else:
            # If no extraction is required, mark all files as available.
            for img in image_files:
                self.__image_handler.file_available(img)

            if self.__current_file.is_dir():
                # if the current_file is a directory then start at the first image
                start_page = 1
            else:
                # Set start_page to the same as current_file.
                start_page = self.__image_files.get_page_from_path(self.__current_file)

        self.__window.set_page(start_page)

    def file_opened(self):
        """
        Called when a new set of files has successfully been opened
        """

        self.__file_loaded = True

        self.__events.run_events(EventType.FILE_OPENED)

    def file_closed(self):
        """
        Called when the current file has been closed
        """

        self.__events.run_events(EventType.FILE_CLOSED)

    def close_file(self):
        """
        Close the currently opened file and its provider
        """

        self._close(close_provider=True)

    def _close(self, close_provider: bool = False):
        """
        Run tasks for "closing" the currently opened file(s)
        """

        if self.__file_loaded or self.__file_loading:
            if close_provider:
                self.__file_provider = None
            if self.__is_archive:
                self.__extractor.close()
            self.__image_handler.cleanup()
            self.__file_loaded = False
            self.__file_loading = False
            self.__is_archive = False
            self.__current_file = None
            self.__base_path = None
            self.file_closed()

    def _initialize_fileprovider(self, paths: list):
        """
        Initialize the file provider based on the total number of file paths
        in <paths>. If <paths> is a list with more than one entry, assumes that
        only the files in the list should be available. If <paths> is a list with
        a single path, assume that it is either a directory or an image file,
        and all files in that directory should be opened.

        :param path: List of file names, or single file/directory as string.
        """

        self.__file_provider = self.__file_provider_chooser.get_file_provider(paths)

    def _open_archive(self, path: Path):
        """
        Extracts all images in the archive passed in path
        """

        try:
            self.__extractor = Extractor(path)
            self.__extractor.list_contents()
        except Exception as ex:
            logger.error(f'failed to open archive: {path}')
            logger.debug(f'Exception: {ex}')
            raise

    def _file_listed(self, files: list):
        if not self.__file_loading:
            return
        self.__file_loading = False

        self._sort_archive_images(files)
        self._archive_opened(files)

    def _sort_archive_images(self, filelist: list):
        """
        Sorts the image list passed in C{filelist} based on the sorting preference option
        """

        # sort files
        match config['SORT_ARCHIVE_BY']:
            case FileSortType.NAME.value:
                SortAlphanumeric(filelist)
            case FileSortType.NAME_LITERAL.value:
                filelist.sort()

        # sort files order
        if config['SORT_ARCHIVE_ORDER'] == FileSortDirection.DESCENDING.value:
            filelist.reverse()

    def is_file_loaded(self) -> bool:
        return self.__file_loaded

    def is_archive(self):
        """
        Returns True if the current opened file an archive.
        """

        return self.__is_archive

    def get_base_path(self):
        """
        Returns the path to opened archive file, or directory containing current images.
        """

        return self.__base_path

    def _get_file_list(self):
        """
        Get a list of all archives in the same diretory as the opened archive
        """

        return self.__file_provider.list_files(mode=FileTypes.ARCHIVES)

    def get_file_number(self):
        """
        Get the current position of the opened archive and the total archives in the
        current directory. If the current opened file is not an archive do nothing.

        :returns a tuple of (current file number, total files)
        """

        if not self.__is_archive:
            # No file numbers for images.
            return 0, 0

        file_list = self._get_file_list()
        current_index = file_list.index(self.__current_file)

        return current_index + 1, len(file_list)

    def get_real_path(self):
        """
        Return the "real" path to the currently viewed file, i.e. the
        full path to the archive or the full path to the currently viewed image
        """

        if self.__is_archive:
            return self.__base_path

        return self.__image_handler.get_path_to_page()

    def open_archive_direction(self, forward: bool):
        """
        Opens the archive that comes directly after the currently loaded
        archive in that archive's directory listing if forward=True else
        opens the archive that comes directly before the currently loaded
        archive in that archive's directory listing. sorted alphabetically.

        :returns True if a new archive was opened, False otherwise
        """

        if not self.__is_archive:
            return False

        files = self._get_file_list()
        if self.__base_path not in files:
            return False

        current_index = files.index(self.__base_path)

        if forward:
            next_file = files[current_index + 1:]
            next_page = 1
        else:
            next_file = reversed(files[:current_index])
            next_page = self.__open_first_page

        for path in next_file:
            self._close()
            self.open_file(path, next_page)
            return True

        return False

    def _extracted_file(self, filename: Path):
        """
        Called when the extractor finishes extracting the file at
        <name>. This name is relative to the temporary directory
        the files were extracted to
        """

        if not self.__file_loaded:
            return
        self.__events.run_events(EventType.FILE_AVAILABLE, {'filename': filename})
