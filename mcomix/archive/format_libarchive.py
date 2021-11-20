# -*- coding: utf-8 -*-

import libarchive
import os
from pathlib import Path

from mcomix.archive.archive_base import BaseArchive
from mcomix.formats.image import ImageSupported


class LibarchiveExtractor(BaseArchive):
    """
    libarchive file extractor
    """

    __slots__ = ()

    def __init__(self, archive: Path):
        super().__init__(archive)

    def iter_contents(self):
        """
        Generator for listing the archive contents
        """

        with libarchive.file_reader(str(self.archive)) as archive:
            for filename in archive:
                if not filename.isfile:
                    continue
                filepath = Path(filename.pathname)
                if not ImageSupported.is_image_file(filepath):
                    continue
                yield filepath

    def iter_extract(self):
        """
        Generator to extract archive
        """

        # can only extract into CWD
        self._create_directory(self.destination_path)
        os.chdir(self.destination_path)

        with libarchive.file_reader(str(self.archive)) as archive:
            for filename in archive:
                if not filename.isfile:
                    # only extract files, directories will be created
                    # as needed by _create_file()
                    continue
                filepath = Path(filename.pathname)
                if not ImageSupported.is_image_file(filepath):
                    continue
                destination_filepath = Path() / self.destination_path / filepath
                with self._create_file(destination_filepath) as image:
                    for block in filename.get_blocks():
                        image.write(block)
                yield destination_filepath
