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

# must not depend on GTK, or any other optional libraries.

from pathlib import Path

from platformdirs import *

from mcomix.config_backend import ConfigBackend
from mcomix.preferences import config

from mcomix_compiled import ConfigType, PackageInfo

class PreferenceManager:
    def __init__(self):
        super().__init__()

        self.__config_manager = ConfigBackend
        self.__config_path = Path(user_config_dir(PackageInfo.PROG_NAME)) / 'mcomix.toml'

    def load_config_file(self):
        if Path.is_file(self.__config_path):
            saved_prefs = {}
            self.__config_manager.load_config(config=self.__config_path, saved_prefs=saved_prefs)

            for key, value in saved_prefs.items():
                if key in config:
                    config[key] = value

        self.__config_manager.update_config_hash(config=config, module=ConfigType.CONFIG)

    def write_config_file(self):
        self.__config_manager.write_config(config=config, config_path=self.__config_path, module=ConfigType.CONFIG)
