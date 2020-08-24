# -*- coding: utf-8 -*-

import json
from hashlib import sha256
from pathlib import Path

from loguru import logger

from mcomix import constants


class _ConfigManager:
    def __init__(self):
        super().__init__()

        self.config_dir_check()

    @staticmethod
    def config_dir_check():
        if not Path.exists(constants.CONFIG_DIR):
            logger.info(f'Creating missing config dir: {constants.CONFIG_DIR}')
            constants.CONFIG_DIR.mkdir()

        if not Path.exists(constants.DATA_DIR):
            logger.info(f'Creating missing data dir: {constants.DATA_DIR}')
            constants.DATA_DIR.mkdir()

    def hash_config(self, config):
        config_json = self.dump_config(config)
        return sha256(config_json.encode('utf8')).hexdigest()

    @staticmethod
    def dump_config(config):
        return json.dumps(config, ensure_ascii=False, indent=2)

    @staticmethod
    def load_config(config, saved_prefs):
        try:
            with Path.open(config, mode='rt', encoding='utf8') as fd:
                saved_prefs.update(json.load(fd))
        except Exception:
            logger.error('Loading config failed, exiting')
            raise SystemExit

        return saved_prefs

    def write_config(self, config, path):
        config_json = self.dump_config(config)
        path.write_text(config_json)


ConfigManager = _ConfigManager()
