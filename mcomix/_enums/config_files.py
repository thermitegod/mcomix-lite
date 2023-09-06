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

import os
from enum import Enum, auto
from pathlib import Path

from mcomix._enums.mcomix import Mcomix


try:
    class ConfigPaths(Enum):
        HOME = Path.home()

        CONFIG = Path() / os.environ['XDG_CONFIG_HOME'] / Mcomix.PROG_NAME.value
        DATA = Path() / os.environ['XDG_DATA_HOME'] / Mcomix.PROG_NAME.value
        CACHE = Path() / os.environ['XDG_CACHE_HOME'] / Mcomix.PROG_NAME.value
except KeyError:
    class ConfigPaths(Enum):
        HOME = Path.home()

        CONFIG = HOME / '.config' / Mcomix.PROG_NAME.value
        DATA = HOME / '.local/share' / Mcomix.PROG_NAME.value
        CACHE = Path() / '/tmp' / Mcomix.PROG_NAME.value


class ConfigFiles(Enum):
    CONFIG = ConfigPaths.CONFIG.value / 'mcomix.conf'
    KEYBINDINGS = ConfigPaths.CONFIG.value / 'input.conf'
    BOOKMARK = ConfigPaths.DATA.value / 'bookmarks.yml'

class ConfigType(Enum):
    CONFIG = auto()
    KEYBINDINGS = auto()
