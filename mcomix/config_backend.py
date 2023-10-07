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

import hashlib
from datetime import datetime
from pathlib import Path

import tomli, tomli_w

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
        return tomli_w.dumps({'Config': config})

    def load_config(self, config: Path, saved_prefs: dict):
        try:
            contents: str
            with config.open(mode='rt') as fd:
                # not using 'contents' will throw
                # Exception: '_io.TextIOWrapper' object has no attribute 'replace'
                contents = fd.read()
            saved_prefs.update(tomli.loads(contents)['Config'])
        except tomli.TOMLDecodeError as e:
            logger.error('Could not parse TOML config file')
            logger.debug(f'Exception: {e}')
            config.rename(f'{config}.bak-{int(datetime.timestamp(datetime.now()))}')
            return
        except Exception as e:
            logger.error('Loading config failed, exiting')
            logger.debug(f'Exception: {e}')
            config.rename(f'{config}.bak-{int(datetime.timestamp(datetime.now()))}')

    def write_config(self, config: dict, config_path: Path, module: str):
        if self._hash_config(config=config) == self.__stored_config_hash[module]:
            logger.info(f'No changes to write for {module}')
            return

        logger.info(f'Writing changes to {module}')
        config_path.write_text(self._dump_config(config))


ConfigBackend = _ConfigBackend()
