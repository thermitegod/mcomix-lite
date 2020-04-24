# -*- coding: utf-8 -*-

"""file_provider.py - Handles listing files for the current directory and
switching to the next/previous directory"""

import functools
from pathlib import Path

from loguru import logger

from mcomix import archive_tools, constants, image_tools, tools
from mcomix.preferences import prefs


def get_file_provider(filelist):
    """Initialize a FileProvider with the files in <filelist>.
    If len(filelist) is 1, a OrderedFileProvider will be constructed, which
    will simply open all files in the passed directory.
    If len(filelist) is greater 1, a PreDefinedFileProvider will be created,
    which will only ever list the files that were passed into it.
    If len(filelist) is zero, FileProvider will look at the last file opened,
    if "Auto Open last file" is set. Otherwise, no provider is constructed"""
    if len(filelist) > 0:
        if len(filelist) == 1:
            if Path(filelist[0]).exists:
                return OrderedFileProvider(filelist[0])
            return None
        return PreDefinedFileProvider(filelist)
    return None


class FileProvider:
    """Base class for various file listing strategies"""
    # Constants for determining which files to list.
    IMAGES, ARCHIVES = 1, 2

    def set_directory(self, file_or_directory):
        pass

    def get_directory(self):
        return Path.cwd()

    def list_files(self, mode=IMAGES):
        return []

    def next_directory(self):
        return False

    def previous_directory(self):
        return False

    @staticmethod
    def sort_files(files):
        """Sorts a list of C{files} depending on the current preferences. The list is sorted in-place"""
        if prefs['sort by'] == constants.SORT_NAME:
            tools.alphanumeric_sort(files)
        elif prefs['sort by'] == constants.SORT_LAST_MODIFIED:
            # Most recently modified file first
            files.sort(key=lambda filename: Path.stat(filename).st_mtime * -1)
        elif prefs['sort by'] == constants.SORT_SIZE:
            # Smallest file first
            files.sort(key=lambda filename: Path.stat(filename).st_size)
        # else: don't sort at all: use OS ordering.

        # Default is ascending.
        if prefs['sort order'] == constants.SORT_DESCENDING:
            files.reverse()


class OrderedFileProvider(FileProvider):
    """This provider will list all files in the same directory as the one passed to the constructor"""

    def __init__(self, file_or_directory):
        """Initializes the file listing. If <file_or_directory> is a file,
        directory will be used as base path. If it is a directory, that
        will be used as base file"""
        self.set_directory(file_or_directory)

        self.__base_dir = self.__base_dir

    def set_directory(self, file_or_directory):
        """Sets the base directory"""
        file_or_directory = Path(file_or_directory)
        if Path.is_dir(file_or_directory):
            directory = file_or_directory
        elif Path.is_file(file_or_directory):
            directory = Path(file_or_directory).parent
        else:
            # Passed file doesn't exist
            raise ValueError(f'Invalid path: "{file_or_directory}"')

        self.__base_dir = Path.resolve(directory)

    def get_directory(self):
        return self.__base_dir

    def list_files(self, mode=FileProvider.IMAGES):
        """Lists all files in the current directory. Returns a list of absolute paths, already sorted"""
        if mode == FileProvider.IMAGES:
            should_accept = functools.partial(image_tools.is_image_file, check_mimetype=True)
        elif mode == FileProvider.ARCHIVES:
            should_accept = archive_tools.is_archive_file
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

    def next_directory(self):
        """Switches to the next sibling directory. Next call to
        list_file() returns files in the new directory.
        Returns True if the directory was changed, otherwise False"""
        if len(directories := self.__get_sibling_directories(self.__base_dir)) - 1 \
                > (current_index := directories.index(self.__base_dir)):
            self.__base_dir = directories[current_index + 1]
            return True

        return False

    def previous_directory(self):
        """Switches to the previous sibling directory. Next call to
        list_file() returns files in the new directory.
        Returns True if the directory was changed, otherwise False"""
        directories = self.__get_sibling_directories(self.__base_dir)
        if (current_index := directories.index(self.__base_dir)) > 0:
            self.__base_dir = directories[current_index - 1]
            return True

        return False

    @staticmethod
    def __get_sibling_directories(dir):
        """Returns a list of all sibling directories of <dir>, already sorted"""
        parent_dir = Path(dir).dirname

        directories = []
        for directory in Path(parent_dir).iterdir():
            sibling_dir = Path() / parent_dir / directory
            if Path.is_dir(sibling_dir):
                directories.update(sibling_dir)

        return tools.alphanumeric_sort(directories)


class PreDefinedFileProvider(FileProvider):
    """Returns only a list of files as passed to the constructor"""

    def __init__(self, files):
        """<files> is a list of files that should be shown. The list is filtered
        to contain either only images, or only archives, depending on what the first
        file is, since FileHandler will probably have problems of archives and images
        are mixed in a file list"""
        should_accept = self.__get_file_filter(files)

        self.__files = []

        for file in files:
            if Path.is_dir(file):
                provider = OrderedFileProvider(file)
                self.__files.extend(provider.list_files())

            elif should_accept(file):
                self.__files.append(str(file))

    def list_files(self, mode=FileProvider.IMAGES):
        """Returns the files as passed to the constructor"""
        return self.__files

    @staticmethod
    def __get_file_filter(files):
        """Determines what kind of files should be filtered in the given list
        of <files>. Returns either a filter accepting only images, or only archives,
        depending on what type of file is found first in the list"""
        for file in files:
            if Path.is_file(file):
                if image_tools.is_image_file(file):
                    return image_tools.is_image_file
                if archive_tools.is_archive_file(file):
                    return archive_tools.is_archive_file

        # Default filter only accepts images.
        return image_tools.is_image_file
