# -*- coding: utf-8 -*-

import functools
from pathlib import Path

from loguru import logger

from mcomix.archive_tools import ArchiveTools
from mcomix.constants import Constants
from mcomix.image_tools import ImageTools
from mcomix.providers.file_provider_base import FileProvider
from mcomix.sort_alphanumeric import SortAlphanumeric


class OrderedFileProvider(FileProvider):
    """
    This provider will list all files in the same directory as the one passed to the constructor
    """

    def __init__(self, path: Path):
        """
        Initializes the file listing. If <file_or_directory> is a file,
        directory will be used as base path. If it is a directory, that
        will be used as base file
        """

        super().__init__()

        self.__base_dir = self.set_directory(path)

    def get_directory(self):
        return self.__base_dir

    def list_files(self, mode: int):
        """
        Lists all files in the current directory. Returns a list of absolute paths, already sorted
        """

        if mode == Constants.FILE_TYPE['IMAGES']:
            should_accept = functools.partial(ImageTools.is_image_file, check_mimetype=True)
        elif mode == Constants.FILE_TYPE['ARCHIVES']:
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
                    fname_map[fpath] = fn
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

            SortAlphanumeric(dirs)
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
