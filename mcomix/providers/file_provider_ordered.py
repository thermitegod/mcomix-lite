# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.archive_tools import ArchiveTools
from mcomix.constants import Constants
from mcomix.image_tools import ImageTools
from mcomix.preferences import config
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
            should_accept = ImageTools.is_image_file
        elif mode == Constants.FILE_TYPE['ARCHIVES']:
            should_accept = ArchiveTools.is_archive_file
        else:
            raise ValueError

        files = []
        for fn in Path(self.__base_dir).iterdir():
            if should_accept(fn):
                files.append(fn)

        self._sort_files(files)

        return files

    @staticmethod
    def _sort_files(files: list):
        """
        Sorts a list of C{files} depending on the current preferences. The list is sorted in-place
        """

        if config['SORT_BY'] == Constants.FILE_SORT_TYPE['NAME']:
            SortAlphanumeric(files)
        elif config['SORT_BY'] == Constants.FILE_SORT_TYPE['LAST_MODIFIED']:
            # Most recently modified file first
            files.sort(key=lambda filename: Path.stat(filename).st_mtime * -1)
        elif config['SORT_BY'] == Constants.FILE_SORT_TYPE['SIZE']:
            # Smallest file first
            files.sort(key=lambda filename: Path.stat(filename).st_size)
        else:
            # don't sort at all: use arbitrary ordering.
            pass

        # Default is ascending.
        if config['SORT_ORDER'] == Constants.FILE_SORT_DIRECTION['DESCENDING']:
            files.reverse()
