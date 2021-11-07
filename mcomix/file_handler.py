# -*- coding: utf-8 -*-

"""file_handler.py - File handler that takes care of opening archives and images"""

from __future__ import annotations

from pathlib import Path

from gi.repository import Gtk
from loguru import logger

from mcomix.archive_extractor import Extractor
from mcomix.enums.file_sort import FileSortDirection, FileSortType
from mcomix.enums.file_types import FileTypes
from mcomix.formats.archive import ArchiveSupported
from mcomix.file_provider import GetFileProvider
from mcomix.lib.callback import Callback
from mcomix.preferences import config
from mcomix.sort.sort_alphanumeric import SortAlphanumeric

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class FileHandler:
    """
    The FileHandler keeps track of the actual files/archives opened.
    While ImageHandler takes care of pages/images, this class provides
    the raw file names for archive members and image files, extracts
    archives, and lists directories for image files
    """

    def __init__(self, window: MainWindow):
        super().__init__()

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
        self.__extractor = Extractor()
        self.__extractor.file_extracted += self._extracted_file
        self.__extractor.contents_listed += self._listed_contents
        #: Provides a list of available files/archives in the open directory.
        self.__file_provider_chooser = GetFileProvider()
        self.__file_provider = None

        self.__start_page = 0

        self.__open_first_page = None

        self.update_opening_behavior()

    def update_opening_behavior(self):
        self.__open_first_page = 0 if config['OPEN_FIRST_PAGE'] else -1

    def refresh_file(self, *args, **kwargs):
        """
        Closes the current file(s)/archive and reloads them
        """

        if self.__file_loaded:
            current_file = self.get_real_path()
            if self.__is_archive:
                start_page = self.__window.imagehandler.get_current_page()
            else:
                start_page = 0
            self.open_file(current_file, start_page)

    def open_file(self, path: Path, start_page: int = 0):
        """
        Open the file pointed to by <path>.
        If <start_page> is not set we set the current
        page to 1 (first page), if it is set we set the current page to the
        value of <start_page>. If <start_page> is non-positive it means the
        last image.

        :returns: True if the file is successfully loaded.
        """

        self._close()

        self.__is_archive = ArchiveSupported.is_archive_file(path)
        self.__start_page = start_page
        self.__current_file = path

        # Actually open the file(s)/archive passed in path.
        if self.__is_archive:
            self._open_archive(self.__current_file)
            self.__file_loading = True
        else:
            image_files = self.__file_provider.list_files(mode=FileTypes.IMAGES)
            self.__base_path = self.__file_provider.get_directory()
            self._archive_opened(image_files)

        return True

    def _archive_opened(self, image_files: list):
        """
        Called once the archive has been opened and its contents listed
        """

        self.__window.imagehandler.set_image_files(image_files)
        self.file_opened()

        if not image_files:
            logger.error(f'No images in "{self.__current_file.name}"')
            return

        if not self.__is_archive:
            # If no extraction is required, mark all files as available.
            for img in image_files:
                self.file_available(img)

            # Set current page to current file.
            if self.__current_file in image_files:
                current_image_index = image_files.index(self.__current_file)
            else:
                current_image_index = 0
        else:
            self.__extractor.extract()
            last_image_index = self._get_index_for_page(self.__start_page, len(image_files))

            if self.__start_page:
                current_image_index = last_image_index
            else:
                # Don't switch to last page yet; since we have not asked
                # the user for confirmation yet.
                current_image_index = 0

            if last_image_index != current_image_index:
                # Bump last page closer to the front of the extractor queue.
                self.__window.set_page(last_image_index + 1)

        self.__window.set_page(current_image_index + 1)

    @Callback
    def file_opened(self):
        """
        Called when a new set of files has successfully been opened
        """

        self.__file_loaded = True

    @Callback
    def file_closed(self):
        """
        Called when the current file has been closed
        """

        pass

    def close_file(self, *args):
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
            self.__window.imagehandler.cleanup()
            self.__file_loaded = False
            self.__file_loading = False
            self.__is_archive = False
            self.__current_file = None
            self.__base_path = None
            self.file_closed()

        # Catch up on UI events, so we don't leave idle callbacks.
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)

    def initialize_fileprovider(self, path: list):
        """
        Creates the L{file_provider.FileProvider} for C{path}.
        If C{path} is a list, assumes that only the files in the list
        should be available. If C{path} is a string, assume that it is
        either a directory or an image file, and all files in that directory should be opened.

        :param path: List of file names, or single file/directory as string.
        """

        self.__file_provider = self.__file_provider_chooser.get_file_provider(path)

    def _open_archive(self, path: Path):
        """
        Opens the archive passed in C{path}.
        Creates an L{archive_extractor.Extractor} and extracts all images
        found within the archive.

        :returns: A tuple containing C{(image_files, image_index)}
        """

        self.__base_path = path
        try:
            self.__extractor.setup(self.__base_path)
        except Exception as ex:
            logger.error(f'failed to open archive: {self.__base_path}')
            logger.error(f'Exception: {ex}')
            raise

    def _listed_contents(self, extractor, image_files: list):
        if not self.__file_loading:
            return
        self.__file_loading = False

        self._sort_archive_images(image_files)
        self._archive_opened(image_files)

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

    def _get_index_for_page(self, start_page: int, num_of_pages: int):
        """
        Returns the page that should be displayed for an archive.

        :param start_page: If -1, show last page. If 0, show first page.
                           If > 0, show C{start_page}.
        :param num_of_pages: Page count.
        :returns: page index
        """

        if start_page < 0:
            if config['DEFAULT_DOUBLE_PAGE']:
                current_image_index = num_of_pages - 2
            else:
                current_image_index = num_of_pages - 1
        else:
            current_image_index = start_page - 1

        return min(max(0, current_image_index), num_of_pages - 1)

    def get_file_loaded(self):
        return self.__file_loaded

    def is_archive(self):
        return self.__is_archive

    def get_base_path(self):
        return self.__base_path

    def _get_file_list(self):
        return self.__file_provider.list_files(mode=FileTypes.ARCHIVES)

    def get_file_number(self):
        if not self.__is_archive:
            # No file numbers for images.
            return 0, 0

        file_list = self._get_file_list()
        if self.__current_file in file_list:
            current_index = file_list.index(self.__current_file)
        else:
            current_index = 0
        return current_index + 1, len(file_list)

    def get_current_filename(self):
        """
        Return a string with the name of the currently viewed file that is suitable for printing

        :returns: name of the currently viewed file
        """

        if self.__is_archive:
            return self.__base_path.name

        return self.__base_path.parent

    def get_real_path(self):
        """
        Return the "real" path to the currently viewed file, i.e. the
        full path to the archive or the full path to the currently viewed image
        """

        if self.__is_archive:
            return self.__base_path

        return self.__window.imagehandler.get_path_to_page()

    def open_archive_direction(self, forward: bool, *args):
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
            return

        current_index = files.index(self.__base_path)

        if forward:
            next_file = files[current_index + 1:]
            next_page = 0
        else:
            next_file = reversed(files[:current_index])
            next_page = self.__open_first_page

        for path in next_file:
            if not path.is_file():
                return False

            if ArchiveSupported.is_archive_file(path=path):
                self._close()
                self.open_file(path, next_page)
                return True

    @Callback
    def file_available(self, filepath: str):
        """
        Called every time a new file from the Filehandler's opened
        files becomes available. C{filepaths} is a list of now available files
        """

        pass

    def _extracted_file(self, extractor, name: str):
        """
        Called when the extractor finishes extracting the file at
        <name>. This name is relative to the temporary directory
        the files were extracted to
        """

        if not self.__file_loaded:
            return
        self.file_available(name)
