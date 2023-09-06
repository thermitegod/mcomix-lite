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

from enum import Enum
from pathlib import Path


class ArchiveSupported(Enum):
    EXTS = set(
        (
            '.zip', '.cbz',
            '.rar', '.cbr',
            '.7z', '.cb7',
            '.tar', '.cbt',
            '.gz', '.bz2', '.lzma', '.xz', '.lz4', '.zst',
            '.lrzip', '.lzip',
            '.lha', '.lzh',
        )
    )

    @classmethod
    def is_archive_file(cls, path: Path):
        return path.suffix.lower() in cls.EXTS.value
