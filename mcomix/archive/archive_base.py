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

from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from mcomix.enums import ConfigPaths


class BaseArchive:
    """
    Base archive interface.
    """

    def __init__(self, archive: Path):
        super().__init__()

        self.archive = archive

        if not Path.exists(ConfigPaths.CACHE.value):
            ConfigPaths.CACHE.value.mkdir(parents=True, exist_ok=True)

        self.tempdir = TemporaryDirectory(dir=ConfigPaths.CACHE.value)
        self.destination_path = Path() / self.tempdir.name / 'main_archive'

    def iter_contents(self):
        """
        Generator for listing the archive contents
        """

        raise NotImplementedError

    def iter_extract(self):
        """
        Generator to extract <wanted> from archive to <destination_dir>

        :param wanted: files to extract
        :param destination_dir: extraction path
        """

        raise NotImplementedError

    def close(self):
        """
        Closes the archive and releases held resources
        """

        logger.debug(f'Cleanup TemporaryDirectory: \'{self.tempdir}\'')
        self.tempdir.cleanup()

    def _create_directory(self, path: Path):
        """
        Recursively create a directory if it doesn't exist yet
        """

        if path.is_dir():
            return

        path.mkdir(parents=True, exist_ok=True)

    def _create_file(self, path: Path):
        """
        Open <dst_path> for writing, making sure base directory exists

        :returns: created image path
        """

        # recreate the archives directory structure,
        # needed for archives that are not flat
        self._create_directory(path.parent)

        return Path.open(path, mode='wb')
