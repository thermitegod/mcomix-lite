# -*- coding: utf-8 -*-

"""file_provider.py - Handles listing files for the current directory and
switching to the next/previous directory"""

from pathlib import Path

from loguru import logger

from mcomix.constants import Constants
from mcomix.preferences import config
from mcomix.sort_alphanumeric import SortAlphanumeric


class FileProvider:
    """
    Base class for various file listing strategies
    """

    def __init__(self):
        super().__init__()

    def set_directory(self, path: str):
        """
        Sets the base directory
        """

        file_or_directory = Path(path).resolve()
        if Path.is_dir(file_or_directory):
            return file_or_directory
        elif Path.is_file(file_or_directory):
            return file_or_directory.parent
        else:
            logger.error(f'Invalid path: \'{file_or_directory}\'')
            raise ValueError

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
