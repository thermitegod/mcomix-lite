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

from bytesize import Size

from loguru import logger

from mcomix.preferences import config


def format_filesize(path: Path) -> str:
    try:
        size = Path.stat(path).st_size
    except (AttributeError, FileNotFoundError):
        logger.warning(f'failed to get file size for: {path}')
        return 'unknown'

    return f'{Size(size).human_readable(max_places=3)}'
