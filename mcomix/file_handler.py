# -*- coding: utf-8 -*-

"""file_handler.py - File handler that takes care of opening archives and images"""

import os
from pathlib import Path

from gi.repository import Gtk
from loguru import logger

from mcomix import archive_tools, constants, image_tools, file_provider
from mcomix.archive_extractor import Extractor
from mcomix.file_provider import FileProvider
from mcomix.lib.callback import Callback
from mcomix.preferences import prefs


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
        #: Temporary directory used for extracting archives.
        self.__tmp_dir = None
        #: If C{True}, no longer wait for files to get extracted.
        self.__stop_waiting = False
        #: Mapping of absolute paths to archive path names.
        self.__name_table = {}
        #: Archive extractor.
        self.__extractor = Extractor()
        self.__extractor.file_extracted += self._extracted_file
        self.__extractor.contents_listed += self._listed_contents
        #: Condition to wait on when extracting archives and waiting on files.
        self.__condition = None
        #: Provides a list of available files/archives in the open directory.
        self.__file_provider = None

        self.__filelist = None
        self.__start_page = 0

        self.__open_first_page = 0 if prefs['open first page'] else -1

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
            self.open_file(current_file, start_page, keep_fileprovider=True)

    def open_file(self, path: list, start_page: int = 0, keep_fileprovider: bool = False):
        """
        Open the file pointed to by <path>.
        If <start_page> is not set we set the current
        page to 1 (first page), if it is set we set the current page to the
        value of <start_page>. If <start_page> is non-positive it means the
        last image.

        :returns: True if the file is successfully loaded.
        """

        self._close()

        try:
            path = Path() / self._initialize_fileprovider(path, keep_fileprovider)
        except ValueError as ex:
            ex = str(ex)
            logger.error(ex)
            self.__window.statusbar.set_message(ex)
            return False

        error_message = self._check_access(path)
        if error_message:
            logger.error(error_message)
            self.__window.statusbar.set_message(error_message)
            self.file_opened()
            return False

        self.__filelist = self.__file_provider.list_files()
        self.__archive_type = archive_tools.archive_mime_type(path)
        self.__start_page = start_page
        self.__current_file = str(path)
        self.__stop_waiting = False

        # Actually open the file(s)/archive passed in path.
        if self.__archive_type is not None:
            try:
                self._open_archive(self.__current_file)
            except Exception as ex:
                ex = str(ex)
                logger.error(ex)
                self.__window.statusbar.set_message(ex)
                self.file_opened()
                return False
            self.__file_loading = True
        else:
            image_files, current_image_index = self._open_image_files(self.__filelist, self.__current_file)
            self._archive_opened(image_files)

        return True

    def _archive_opened(self, image_files: list):
        """
        Called once the archive has been opened and its contents listed
        """

        self.__window.imagehandler.set_base_path(self.__base_path)
        self.__window.imagehandler.set_image_files(image_files)
        self.file_opened()

        if not image_files:
            msg = f'No images in "{Path(self.__current_file).name}"'
            logger.error(msg)
            self.__window.statusbar.set_message(msg)

        else:
            if self.__archive_type is None:
                # If no extraction is required, mark all files as available.
                self.file_available(self.__filelist)
                # Set current page to current file.
                if self.__current_file in self.__filelist:
                    current_image_index = self.__filelist.index(self.__current_file)
                else:
                    current_image_index = 0
            else:
                self.__extractor.extract()
                last_image_index = self._get_index_for_page(self.__start_page,
                                                            len(image_files),
                                                            self.__current_file)
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
            if self.__archive_type is not None:
                self.__extractor.close()
            self.__window.imagehandler.cleanup()
            self.__file_loaded = False
            self.__file_loading = False
            self.__archive_type = None
            self.__current_file = None
            self.__base_path = None
            self.__stop_waiting = True
            self.__name_table.clear()
            self.file_closed()
        # Catch up on UI events, so we don't leave idle callbacks.
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)

        if self.__tmp_dir is not None:
            self.__tmp_dir = None

    def _initialize_fileprovider(self, path: list, keep_fileprovider: bool):
        """
        Creates the L{file_provider.FileProvider} for C{path}.
        If C{path} is a list, assumes that only the files in the list
        should be available. If C{path} is a string, assume that it is
        either a directory or an image file, and all files in that directory should be opened.

        :param path: List of file names, or single file/directory as string.
        :param keep_fileprovider: If C{True}, no new provider is constructed.
        :returns: If C{path} was a list, returns the first list element. Otherwise, C{path} is not modified
        """

        if isinstance(path, list) and not path:
            assert False, 'Tried to open an empty list of files.'

        elif isinstance(path, list) and len(path) > 0:
            # A list of files was passed - open only these files.
            if self.__file_provider is None or not keep_fileprovider:
                self.__file_provider = file_provider.get_file_provider(path)

            return path[0]
        else:
            # A single file was passed - use Comix' classic open mode
            # and open all files in its directory.
            if self.__file_provider is None or not keep_fileprovider:
                self.__file_provider = file_provider.get_file_provider([path])

            return path

    @staticmethod
    def _check_access(path: Path):
        """
        Checks for various error that could occur when opening C{path}.

        :param path: Path to file that should be opened.
        :return: An appropriate error string, or C{None} if no error was found.
        """

        if not Path.exists(path):
            return f'Could not open {path}: No such file.'
        elif not os.access(path, os.R_OK):
            return f'Could not open {path}: Permission denied.'

        return None

    def _open_archive(self, path: str):
        """
        Opens the archive passed in C{path}.
        Creates an L{archive_extractor.Extractor} and extracts all images
        found within the archive.

        :returns: A tuple containing C{(image_files, image_index)}
        """

        self.__base_path = path
        try:
            self.__condition = self.__extractor.setup(self.__base_path, self.__archive_type)
        except Exception:
            logger.error(f'failed to open archive: {self.__base_path}')
            self.__condition = None
            raise
        self.__tmp_dir = self.__extractor.get_directory()

    def _listed_contents(self, archive, files):
        if not self.__file_loading:
            return
        self.__file_loading = False

        files = self.__extractor.get_files()
        archive_images = [image for image in files
                          if image_tools.is_image_file(image)
                          # Remove MacOS meta files from image list
                          and '__MACOSX' not in image.split('/')]

        self._sort_archive_images(archive_images)

        image_files = archive_images
        self.__name_table = dict(zip(image_files, archive_images))
        self.__extractor.set_files(archive_images)
        self._archive_opened(image_files)

    @staticmethod
    def _sort_archive_images(filelist: list):
        """
        Sorts the image list passed in C{filelist} based on the sorting preference option
        """

        if prefs['sort archive by'] == constants.SORT_NAME:
            file_provider.alphanumeric_sort(filelist)
        elif prefs['sort archive by'] == constants.SORT_NAME_LITERAL:
            filelist.sort()
        else:
            # No sorting
            pass

        if prefs['sort archive order'] == constants.SORT_DESCENDING:
            filelist.reverse()

    @staticmethod
    def _get_index_for_page(start_page: int, num_of_pages: int, path: str):
        """
        Returns the page that should be displayed for an archive.

        :param start_page: If -1, show last page. If 0, show either first page
                           or last read page. If > 0, show C{start_page}.
        :param num_of_pages: Page count.
        :param path: Archive path
        :returns: page index
        :rtype: int
        """

        if start_page < 0 and prefs['default double page']:
            current_image_index = num_of_pages - 2
        elif start_page < 0 and not prefs['default double page']:
            current_image_index = num_of_pages - 1
        else:
            current_image_index = start_page - 1

        return min(max(0, current_image_index), num_of_pages - 1)

    def _open_image_files(self, filelist: list, image_path: str):
        """
        Opens all files passed in C{filelist}.
        If C{image_path} is found in C{filelist}, the current page will be set
        to its index within C{filelist}.

        :returns: Tuple of C{(image_files, image_index)}
        """

        self.__base_path = self.__file_provider.get_directory()

        if image_path in filelist:
            current_image_index = filelist.index(image_path)
        else:
            current_image_index = 0

        return filelist, current_image_index

    def get_file_loaded(self):
        return self.__file_loaded

    def get_archive_type(self):
        return self.__archive_type

    def get_base_path(self):
        return self.__base_path

    def _get_file_list(self):
        return self.__file_provider.list_files(FileProvider.ARCHIVES)

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

        return Path(self.get_path_to_base()).name

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

        if self.__archive_type is not None:
            files = self._get_file_list()
            if self.__base_path not in files:
                return

            current_index = files.index(self.__base_path)

            if forward:
                for path in files[current_index + 1:]:
                    if archive_tools.archive_mime_type(path) is not None:
                        self._close()
                        self.open_file(path, keep_fileprovider=True)
                        return True
            else:
                for path in reversed(files[:current_index]):
                    if archive_tools.archive_mime_type(path) is not None:
                        self._close()
                        self.open_file(path, self.__open_first_page, keep_fileprovider=True)
                        return True

        return False

    def open_directory_direction(self, forward: bool, *args):
        """
        Opens the next sibling directory of the current file if forward=True, else
        opens the previous sibling directory of the current file as specified by file
        provider. Returns True if a new directory was opened and files found

        :param forward: Which direction to open the next archive
        :type forward: bool
        """

        if self.__file_provider is None:
            return

        if self.__archive_type is not None:
            listmode = FileProvider.ARCHIVES
        else:
            listmode = FileProvider.IMAGES

        current_dir = self.__file_provider.get_directory()
        if not self.__file_provider.directory_direction(forward=forward):
            # Restore current directory if no files were found
            self.__file_provider.set_directory(current_dir)
            return False

        self._close()
        files = self.__file_provider.list_files(listmode)
        if len(files) > 0:
            if forward:
                path = files[0]
            else:
                path = files[-1]
        else:
            path = self.__file_provider.get_directory()
        if forward:
            self.open_file(path, keep_fileprovider=True)
        else:
            self.open_file(path, self.__open_first_page, keep_fileprovider=True)
        return True

    @Callback
    def file_available(self, filepaths: list):
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
        self.file_available([name])

    def wait_on_file(self, path):
        """
        Block the running (main) thread if the file <path> is from an
        archive and has not yet been extracted. Return when the file is ready
        """

        if self.__archive_type is None or path is None:
            return

        try:
            name = self.__name_table[path]
            with self.__condition:
                while not self.__extractor.is_ready(name) and not self.__stop_waiting:
                    self.__condition.wait()
        except Exception:
            logger.error(f'Waiting on extraction failed: \'{path}\'')
            return

    def ask_for_files(self, files: list):
        """
        Ask for <files> to be given priority for extraction
        """

        if self.__archive_type is None:
            return

        with self.__condition:
            extractor_files = self.__extractor.get_files()
            for path in reversed(files):
                name = self.__name_table[path]
                if not self.__extractor.is_ready(name):
                    extractor_files.remove(name)
                    extractor_files.insert(0, name)
            self.__extractor.set_files(extractor_files)
