# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.enums import FileSortDirection, FileSortType, FileTypes
from mcomix.formats.archive import ArchiveSupported
from mcomix.formats.image import ImageSupported
from mcomix.preferences import config
from mcomix.providers.file_provider_base import FileProvider
from mcomix.sort.sort_alphanumeric import SortAlphanumeric


class OrderedFileProvider(FileProvider):
    """
    This provider will list all files in the same directory as the one passed to the constructor
    """

    __slots__ = ('__base_dir',)

    def __init__(self, path: Path):
        """
        Initializes the file listing. If <file_or_directory> is a file,
        directory will be used as base path. If it is a directory, that
        will be used as base file
        """

        super().__init__()

        self.__base_dir = self.set_directory(path)

    def list_files(self, mode: int):
        """
        Lists all files in the current directory. Returns a list of absolute paths, already sorted
        """

        match mode:
            case FileTypes.IMAGES:
                should_accept = ImageSupported.is_image_file
            case FileTypes.ARCHIVES:
                should_accept = ArchiveSupported.is_archive_file
            case _:
                raise ValueError

        files = [fn for fn in Path(self.__base_dir).iterdir()
                 if should_accept(fn)]

        self._sort_files(files)

        return files

    def _sort_files(self, files: list):
        """
        Sorts a list of C{files} depending on the current preferences. The list is sorted in-place
        """

        match config['SORT_BY']:
            case FileSortType.NAME.value:
                SortAlphanumeric(files)
            case FileSortType.LAST_MODIFIED.value:
                # Most recently modified file first
                files.sort(key=lambda filename: Path.stat(filename).st_mtime * -1)
            case FileSortType.SIZE.value:
                # Smallest file first
                files.sort(key=lambda filename: Path.stat(filename).st_size)

        # Default is ascending.
        if config['SORT_ORDER'] == FileSortDirection.DESCENDING.value:
            files.reverse()
