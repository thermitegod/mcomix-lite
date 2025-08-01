# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import libarchive
import os
from pathlib import Path

from mcomix.archive.archive_base import BaseArchive

from mcomix_compiled import is_image


class LibarchiveExtractor(BaseArchive):
    """
    libarchive file extractor
    """

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
                if not is_image(filepath):
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
                if not is_image(filepath):
                    continue
                destination_filepath = Path() / self.destination_path / filepath
                with self._create_file(destination_filepath) as image:
                    for block in filename.get_blocks():
                        image.write(block)
                yield destination_filepath
