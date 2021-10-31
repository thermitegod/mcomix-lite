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

        if path.is_dir():
            return path

        return path.parent

    def get_directory(self):
        raise NotImplementedError

    def list_files(self, mode: int):
        raise NotImplementedError
