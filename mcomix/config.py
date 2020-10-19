# -*- coding: utf-8 -*-

import hashlib
import json
from pathlib import Path

from loguru import logger

from mcomix.constants import Constants


class _ConfigManager:
    def __init__(self):
        super().__init__()

        self.stored_config_hash = {
            'preferences': None,
            'keybindings': None,
        }

        self.config_dir_check()

    @staticmethod
    def config_dir_check():
        if not Path.exists(Constants.CONFIG_DIR):
            logger.info(f'Creating missing config dir: {Constants.CONFIG_DIR}')
            Constants.CONFIG_DIR.mkdir()

        if not Path.exists(Constants.DATA_DIR):
            logger.info(f'Creating missing data dir: {Constants.DATA_DIR}')
            Constants.DATA_DIR.mkdir()

    def hash_config(self, config: dict):
        config_json = self.dump_config(config)
        return hashlib.blake2b(config_json.encode('utf8')).hexdigest()

    @staticmethod
    def dump_config(config: dict):
        return json.dumps(config, ensure_ascii=False, indent=2)

    @staticmethod
    def load_config(config: Path, saved_prefs: dict):
        try:
            with Path.open(config, mode='rt', encoding='utf8') as fd:
                saved_prefs.update(json.load(fd))
        except Exception:
            logger.error('Loading config failed, exiting')
            raise SystemExit

    def write_config(self, config: dict, path: Path):
        config_json = self.dump_config(config)
        path.write_text(config_json)


ConfigManager = _ConfigManager()
