# -*- coding: utf-8 -*-

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
