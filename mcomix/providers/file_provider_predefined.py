# -*- coding: utf-8 -*-

from pathlib import Path

from mcomix.enums import FileTypes
from mcomix.formats.archive import ArchiveSupported
from mcomix.formats.image import ImageSupported
from mcomix.providers.file_provider_base import FileProviderBase
from mcomix.providers.file_provider_ordered import OrderedFileProvider


class PreDefinedFileProvider(FileProviderBase):
    """
    Returns only a list of files as passed to the constructor
    """

    def __init__(self, files: list[Path]):
        """
        <files> is a list of files that should be shown. The list is filtered
        to contain either only images, or only archives, depending on what the first
        file is, since FileHandler will probably have problems of archives and images
        are mixed in a file list
        """

        super().__init__()

        should_accept = self._get_file_filter(files)

        for file in files:
            if file.is_dir():
                provider = OrderedFileProvider(file)
                self.files.extend(provider.list_files(mode=FileTypes.IMAGES))

            elif should_accept(file):
                self.files.append(file)

    def list_files(self, mode: int):
        """
        Returns the files as passed to the constructor
        """

        return self.files

    def _get_file_filter(self, files: list[Path]):
        """
        Determines what kind of files should be filtered in the given list
        of <files>. Returns either a filter accepting only images, or only archives,
        depending on what type of file is found first in the list
        """

        for file in files:
            if file.is_file():
                if ImageSupported.is_image_file(file):
                    return ImageSupported.is_image_file
                if ArchiveSupported.is_archive_file(file):
                    return ArchiveSupported.is_archive_file

        # Default filter only accepts images.
        return ImageSupported.is_image_file
