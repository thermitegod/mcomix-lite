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

from loguru import logger

from mcomix.preferences import config


class _FileSize:
    def __init__(self):
        super().__init__()

        if config['SI_UNITS']:
            self.__unit_size = 1000.0
            self.__unit_symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
        else:
            self.__unit_size = 1024.0
            self.__unit_symbols = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')

    def __call__(self, path: Path):
        try:
            n = Path.stat(path).st_size

            s = 0
            while n >= self.__unit_size:
                s += 1
                n /= self.__unit_size

            formated_size = f'{n:.3f} {self.__unit_symbols[s]}'
        except (AttributeError, FileNotFoundError):
            logger.warning(f'failed to get file size for: {path}')
            formated_size = 'unknown'

        return formated_size


FileSize = _FileSize()
