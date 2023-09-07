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

import math
from pathlib import Path

from loguru import logger

from mcomix.preferences import config


def format_filesize(path: Path) -> str:
    if config['SI_UNITS']:
        unit_size = 1000.0
        unit_symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB', 'RB', 'QB')
    else:
        unit_size = 1024.0
        unit_symbols = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB', 'RiB', 'QiB')

    try:
        size = Path.stat(path).st_size
    except (AttributeError, FileNotFoundError):
        logger.warning(f'failed to get file size for: {path}')
        return 'unknown'

    log_size = math.log(size) / math.log(unit_size)
    size_idx = math.floor(log_size)
    unit_size = math.pow(unit_size, log_size - size_idx)
    unit_label = unit_symbols[size_idx]

    return f'{unit_size:.3f} {unit_label}'
