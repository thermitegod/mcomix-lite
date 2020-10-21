# -*- coding: utf-8 -*-

"""file_provider.py - Handles listing files for the current directory and
switching to the next/previous directory"""

import functools
import re
from pathlib import Path

from loguru import logger

from mcomix.archive_tools import ArchiveTools
from mcomix.constants import Constants
from mcomix.image_tools import ImageTools
from mcomix.preferences import config


class SortAlphanumeric:
    def __int__(self):
        super().__init__()

    @staticmethod
    def alphanumeric_sort(filenames: list):
        """
        Do an in-place alphanumeric sort of the strings in <filenames>,
        such that for an example "1.jpg", "2.jpg", "10.jpg" is a sorted ordering
        """

        def keyfunc(s):
            x, y, z = str(s).rpartition('.')
            # re.compile splits into float, int, and characters
            return [p for p in (*re.compile(r'\d+[.]\d+|\d+|\D+').findall(x), z)]

        filenames.sort(key=keyfunc)


class GetFileProvider:
    def __int__(self):
        super().__init__()

    @staticmethod
    def get_file_provider(filelist: list):
        """
        Initialize a FileProvider with the files in <filelist>.
        If len(filelist) is 1, a OrderedFileProvider will be constructed, which
        will simply open all files in the passed directory.
        If len(filelist) is greater 1, a PreDefinedFileProvider will be created,
        which will only ever list the files that were passed into it.
        If len(filelist) is zero, FileProvider will look at the last file opened,
        if "Auto Open last file" is set. Otherwise, no provider is constructed
        """

        if len(filelist) > 0:
            if len(filelist) == 1:
                if Path(filelist[0]).exists:
                    return OrderedFileProvider(filelist[0])
                return None
            return PreDefinedFileProvider(filelist)
        return None


class FileProvider(SortAlphanumeric):
    """
    Base class for various file listing strategies
    """

    def __init__(self):
        super().__init__()

    def set_directory(self, file_or_directory):
        pass

    def get_directory(self):
        return Path.cwd()

    def list_files(self, mode: int):
        return []

    def directory_direction(self, forward: bool):
        return False

    @staticmethod
    def sort_files(files: list):
        """
        Sorts a list of C{files} depending on the current preferences. The list is sorted in-place
        """

        if config['SORT_BY'] == Constants.SORT_NAME:
            SortAlphanumeric.alphanumeric_sort(files)
        elif config['SORT_BY'] == Constants.SORT_LAST_MODIFIED:
            # Most recently modified file first
            files.sort(key=lambda filename: Path.stat(filename).st_mtime * -1)
        elif config['SORT_BY'] == Constants.SORT_SIZE:
            # Smallest file first
            files.sort(key=lambda filename: Path.stat(filename).st_size)
        else:
            # don't sort at all: use arbitrary ordering.
            pass

        # Default is ascending.
        if config['SORT_ORDER'] == Constants.SORT_DESCENDING:
            files.reverse()


class OrderedFileProvider(FileProvider):
    """
    This provider will list all files in the same directory as the one passed to the constructor
    """

    def __init__(self, file_or_directory: str):
        """
        Initializes the file listing. If <file_or_directory> is a file,
        directory will be used as base path. If it is a directory, that
        will be used as base file
        """

        super().__init__()

        self.set_directory(file_or_directory)

        self.__base_dir = self.__base_dir

    def set_directory(self, file_or_directory: str):
        """
        Sets the base directory
        """

        file_or_directory = Path() / file_or_directory
        if Path.is_dir(file_or_directory):
            directory = file_or_directory
        elif Path.is_file(file_or_directory):
            directory = file_or_directory.parent
        else:
            # Passed file doesn't exist
            raise ValueError(f'Invalid path: "{file_or_directory}"')

        self.__base_dir = Path.resolve(directory)

    def get_directory(self):
        return self.__base_dir

    def list_files(self, mode: int):
        """
        Lists all files in the current directory. Returns a list of absolute paths, already sorted
        """

        if mode == Constants.IMAGES:
            should_accept = functools.partial(ImageTools.is_image_file, check_mimetype=True)
        elif mode == Constants.ARCHIVES:
            should_accept = ArchiveTools.is_archive_file
        else:
            should_accept = lambda file: True

        files = []
        fname_map = {}
        try:
            # listdir() return list of bytes only if path is bytes
            for fn in Path(self.__base_dir).iterdir():
                fpath = Path(fn)
                if should_accept(fpath):
                    files.append(fpath)
                    fname_map[fpath] = str(fn)
        except OSError:
            logger.warning(f'Permission denied, Could not open: \'{self.__base_dir}\'')
            return []

        FileProvider.sort_files(files)
        return [fname_map[fpath] for fpath in files]

    def directory_direction(self, forward: bool):
        """
        If forward=True switches to the next sibling directory,
        else Switches to the previous sibling directory. Next call to
        list_file() returns files in the new directory.
        Returns True if the directory was changed, otherwise False
        """

        def __get_sibling_directories(current_dir: Path):
            """
            Returns a list of all sibling directories of <dir>, already sorted
            """

            parent_dir = current_dir.parent

            dirs = []
            for directory in parent_dir.iterdir():
                if Path.is_dir(directory):
                    dirs.append(str(directory))

            SortAlphanumeric.alphanumeric_sort(dirs)
            return directories

        directories = __get_sibling_directories(self.__base_dir)
        current_index = directories.index(str(self.__base_dir))
        if forward:
            if len(directories) - 1 > current_index:
                self.__base_dir = directories[current_index + 1]
                return True
        else:
            if current_index > 0:
                self.__base_dir = directories[current_index - 1]
                return True

        return False


class PreDefinedFileProvider(FileProvider):
    """
    Returns only a list of files as passed to the constructor
    """

    def __init__(self, files: list):
        """
        <files> is a list of files that should be shown. The list is filtered
        to contain either only images, or only archives, depending on what the first
        file is, since FileHandler will probably have problems of archives and images
        are mixed in a file list
        """

        super().__init__()

        should_accept = self.__get_file_filter(files)

        self.__files = []

        for file in files:
            if Path.is_dir(Path(file)):
                provider = OrderedFileProvider(file)
                self.__files.extend(provider.list_files(mode=Constants.IMAGES))

            elif should_accept(file):
                self.__files.append(str(file))

    def list_files(self, mode: int):
        """
        Returns the files as passed to the constructor
        """

        return self.__files

    @staticmethod
    def __get_file_filter(files: list):
        """
        Determines what kind of files should be filtered in the given list
        of <files>. Returns either a filter accepting only images, or only archives,
        depending on what type of file is found first in the list
        """

        for file in files:
            if Path.is_file(Path(file)):
                if ImageTools.is_image_file(file):
                    return ImageTools.is_image_file
                if ArchiveTools.is_archive_file(file):
                    return ArchiveTools.is_archive_file

        # Default filter only accepts images.
        return ImageTools.is_image_file
