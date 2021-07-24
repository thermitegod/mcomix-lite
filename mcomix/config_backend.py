# -*- coding: utf-8 -*-

from pathlib import Path

import xxhash
import yaml
from loguru import logger

from mcomix.constants import Constants


class _ConfigBackend:
    def __init__(self):
        super().__init__()

        self.__stored_config_hash = {
            'preferences': None,
            'keybindings': None,
        }

        if not Path.exists(Constants.PATHS['CONFIG']):
            logger.info(f'Creating missing config dir')
            Constants.PATHS['CONFIG'].mkdir()

        if not Path.exists(Constants.PATHS['DATA']):
            logger.info(f'Creating missing data dir')
            Constants.PATHS['DATA'].mkdir()

    def update_config_hash(self, config: dict, module: str):
        self.__stored_config_hash[module] = self._hash_config(config=config)

    def _hash_config(self, config: dict):
        return xxhash.xxh3_64(self._dump_config(config).encode('utf8')).hexdigest()

    @staticmethod
    def _dump_config(config: dict):
        return yaml.dump(config, Dumper=yaml.CSafeDumper, sort_keys=False)

    @staticmethod
    def load_config(config: Path, saved_prefs: dict):
        try:
            with Path.open(config, mode='rt', encoding='utf8') as fd:
                saved_prefs.update(yaml.safe_load(fd))
        except Exception as ex:
            logger.error('Loading config failed, exiting')
            logger.error(f'Exception: {ex}')
            raise SystemExit

    def write_config(self, config: dict, config_path: Path, module: str):
        if self._hash_config(config=config) == self.__stored_config_hash[module]:
            logger.info(f'No changes to write for {module}')
            return

        logger.info(f'Writing changes to {module}')
        config_path.write_text(self._dump_config(config))


ConfigBackend = _ConfigBackend()
