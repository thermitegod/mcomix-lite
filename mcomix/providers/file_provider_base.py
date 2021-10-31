# -*- coding: utf-8 -*-

"""file_provider.py - Handles listing files for the current directory and
switching to the next/previous directory"""

from pathlib import Path

from loguru import logger


class FileProvider:
    """
    Base class for various file listing strategies
    """

    def __init__(self):
        super().__init__()

    def set_directory(self, path: Path):
        """
        Sets the base directory
        """

        if Path.is_dir(path):
            return path
        elif Path.is_file(path):
            return path.parent
        else:
            logger.error(f'Invalid path: \'{path}\'')
            raise ValueError

    def get_directory(self):
        raise NotImplementedError

    def list_files(self, mode: int):
        raise NotImplementedError
