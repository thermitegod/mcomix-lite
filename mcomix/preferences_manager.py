# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

from pathlib import Path

from loguru import logger

from mcomix.config import ConfigManager
from mcomix.constants import Constants
from mcomix.preferences import config


class _PreferenceManager:
    def __init__(self):
        super().__init__()

        self.__preference_path = Constants.PREFERENCE_PATH

    def load_preferences_file(self):
        saved_prefs = {}
        if Path.is_file(self.__preference_path):
            ConfigManager.load_config(config=self.__preference_path, saved_prefs=saved_prefs)

        config.update(filter(lambda i: i[0] in config, saved_prefs.items()))

        ConfigManager.stored_config_hash['preferences'] = ConfigManager.hash_config(config)

    def write_preferences_file(self):
        config_hash = ConfigManager.hash_config(config=config)
        if config_hash == ConfigManager.stored_config_hash['preferences']:
            logger.info('No changes to write for preferences')
            return

        logger.info('Writing changes to preferences')

        ConfigManager.stored_config_hash['preferences'] = config_hash
        ConfigManager.write_config(config=config, path=self.__preference_path)


PreferenceManager = _PreferenceManager()
