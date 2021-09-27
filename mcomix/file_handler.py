# -*- coding: utf-8 -*-

"""file_handler.py - File handler that takes care of opening archives and images"""

from pathlib import Path

from gi.repository import Gtk
from loguru import logger

from mcomix.archive_extractor import Extractor
from mcomix.archive_tools import ArchiveTools
from mcomix.constants import Constants
from mcomix.file_provider import GetFileProvider
from mcomix.image_tools import ImageTools
from mcomix.lib.callback import Callback
from mcomix.preferences import config
from mcomix.sort.sort_alphanumeric import SortAlphanumeric


class FileHandler:
    """
    The FileHandler keeps track of the actual files/archives opened.
    While ImageHandler takes care of pages/images, this class provides
    the raw file names for archive members and image files, extracts
    archives, and lists directories for image files
    """

    def __init__(self, window):
        super().__init__()

        #: Indicates if files/archives are currently loaded/loading.
        self.__file_loaded = False
        self.__file_loading = False
        #: None if current file is not an archive, or unrecognized format.
        self.__archive_type = None

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
        self.__file_provider = None

        self.__filelist = None
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
            current_file = Path.resolve(Path(self.__window.imagehandler.get_real_path()))
            if self.__archive_type is not None:
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

        self.__filelist = self.__file_provider.list_files(mode=Constants.FILE_TYPE['IMAGES'])
        self.__archive_type = ArchiveTools.archive_mime_type(path)
        self.__start_page = start_page
        self.__current_file = path

        # Actually open the file(s)/archive passed in path.
        if self.__archive_type is not None:
            self._open_archive(self.__current_file)
            self.__file_loading = True
        else:
            self.__base_path = self.__file_provider.get_directory()
            self._archive_opened(self.__filelist)

        return True

    def _archive_opened(self, image_files: list):
        """
        Called once the archive has been opened and its contents listed
        """

        self.__window.imagehandler.set_base_path(self.__base_path)
        self.__window.imagehandler.set_image_files(image_files)
        self.file_opened()

        if not image_files:
            logger.error(f'No images in "{self.__current_file.name}"')
            return

        if self.__archive_type is None:
            # If no extraction is required, mark all files as available.
            for img in self.__filelist:
                self.file_available(img)

            # Set current page to current file.
            if self.__current_file in self.__filelist:
                current_image_index = self.__filelist.index(self.__current_file)
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
            if self.__archive_type is not None:
                self.__extractor.close()
            self.__window.imagehandler.cleanup()
            self.__file_loaded = False
            self.__file_loading = False
            self.__archive_type = None
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

        self.__file_provider = GetFileProvider.get_file_provider(path)

    def _open_archive(self, path: Path):
        """
        Opens the archive passed in C{path}.
        Creates an L{archive_extractor.Extractor} and extracts all images
        found within the archive.

        :returns: A tuple containing C{(image_files, image_index)}
        """

        self.__base_path = path
        try:
            self.__extractor.setup(self.__base_path, self.__archive_type)
        except Exception as ex:
            logger.error(f'failed to open archive: {self.__base_path}')
            logger.error(f'Exception: {ex}')
            raise

    def _listed_contents(self, archive, files):
        if not self.__file_loading:
            return
        self.__file_loading = False

        archive_images = [image for image in files
                          if ImageTools.is_image_file(Path(image))
                          and not image.endswith('.pdf')]

        self._sort_archive_images(archive_images)
        self.__extractor.set_files(archive_images)
        self._archive_opened(archive_images)

    @staticmethod
    def _sort_archive_images(filelist: list):
        """
        Sorts the image list passed in C{filelist} based on the sorting preference option
        """

        if config['SORT_ARCHIVE_BY'] == Constants.FILE_SORT_TYPE['NAME']:
            SortAlphanumeric(filelist)
        elif config['SORT_ARCHIVE_BY'] == Constants.FILE_SORT_TYPE['NAME_LITERAL']:
            filelist.sort()
        else:
            # No sorting
            pass

        if config['SORT_ARCHIVE_ORDER'] == Constants.FILE_SORT_DIRECTION['DESCENDING']:
            filelist.reverse()

    @staticmethod
    def _get_index_for_page(start_page: int, num_of_pages: int):
        """
        Returns the page that should be displayed for an archive.

        :param start_page: If -1, show last page. If 0, show either first page
                           or last read page. If > 0, show C{start_page}.
        :param num_of_pages: Page count.
        :param path: Archive path
        :returns: page index
        """

        if start_page < 0 and config['DEFAULT_DOUBLE_PAGE']:
            current_image_index = num_of_pages - 2
        elif start_page < 0 and not config['DEFAULT_DOUBLE_PAGE']:
            current_image_index = num_of_pages - 1
        else:
            current_image_index = start_page - 1

        return min(max(0, current_image_index), num_of_pages - 1)

    def get_file_loaded(self):
        return self.__file_loaded

    def get_archive_type(self):
        return self.__archive_type

    def get_base_path(self):
        return self.__base_path

    def _get_file_list(self):
        return self.__file_provider.list_files(mode=Constants.FILE_TYPE['ARCHIVES'])

    def get_file_number(self):
        if self.__archive_type is None:
            # No file numbers for images.
            return 0, 0

        file_list = self._get_file_list()
        if self.__current_file in file_list:
            current_index = file_list.index(self.__current_file)
        else:
            current_index = 0
        return current_index + 1, len(file_list)

    def get_path_to_base(self):
        """
        Return the full path to the current base (path to archive or image directory.)
        """

        if self.__archive_type is not None:
            return self.__base_path

        filename = Path() / self.__window.imagehandler.get_current_path()
        if filename:
            return filename.parent

        return None

    def get_base_filename(self):
        """
        Return the filename of the current base (archive filename or directory name)

        :returns: filename of the current base
        """

        return self.get_path_to_base().name

    def get_current_filename(self):
        """
        Return a string with the name of the currently viewed file that is suitable for printing

        :returns: name of the currently viewed file
        """

        return self.__window.imagehandler.get_current_filename()

    def open_archive_direction(self, forward: bool, *args):
        """
        Opens the archive that comes directly after the currently loaded
        archive in that archive's directory listing if forward=True else
        opens the archive that comes directly before the currently loaded
        archive in that archive's directory listing. sorted alphabetically.

        :returns True if a new archive was opened, False otherwise
        """

        if self.__archive_type is None:
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

            if ArchiveTools.is_archive_file(path=path):
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
