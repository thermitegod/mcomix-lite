# -*- coding: utf-8 -*-

import libarchive
import os
from pathlib import Path

from mcomix.archive.archive_base import BaseArchive


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
                yield Path(filename.pathname)

    def iter_extract(self):
        """
        Generator to extract archive to <destination_dir>

        :param destination_dir: extraction path
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
                destination_file_path = Path() / self.destination_path / filename.pathname
                with self._create_file(destination_file_path) as image:
                    for block in filename.get_blocks():
                        image.write(block)
                yield destination_file_path
