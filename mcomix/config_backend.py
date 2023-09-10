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

import hashlib
import yaml
from loguru import logger

from mcomix.enums import ConfigPaths, ConfigType


class _ConfigBackend:
    def __init__(self):
        super().__init__()

        self.__stored_config_hash = {
            ConfigType.CONFIG: None,
            ConfigType.KEYBINDINGS: None,
        }

        if not Path.exists(ConfigPaths.CONFIG.value):
            logger.info('Creating missing config dir')
            ConfigPaths.CONFIG.value.mkdir()

        if not Path.exists(ConfigPaths.DATA.value):
            logger.info('Creating missing data dir')
            ConfigPaths.DATA.value.mkdir()

    def update_config_hash(self, config: dict, module: str):
        self.__stored_config_hash[module] = self._hash_config(config=config)

    def _hash_config(self, config: dict):
        return hashlib.sha1(self._dump_config(config).encode('utf8')).hexdigest()

    def _dump_config(self, config: dict):
        return yaml.dump(config, Dumper=yaml.CSafeDumper, sort_keys=False)

    def load_config(self, config: Path, saved_prefs: dict):
        try:
            with Path.open(config, mode='rt', encoding='utf8') as fd:
                saved_prefs.update(yaml.safe_load(fd))
        except Exception as ex:
            logger.error('Loading config failed, exiting')
            logger.debug(f'Exception: {ex}')
            raise SystemExit

    def write_config(self, config: dict, config_path: Path, module: str):
        if self._hash_config(config=config) == self.__stored_config_hash[module]:
            logger.info(f'No changes to write for {module}')
            return

        logger.info(f'Writing changes to {module}')
        config_path.write_text(self._dump_config(config))


ConfigBackend = _ConfigBackend()
