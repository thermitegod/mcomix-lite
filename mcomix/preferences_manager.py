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

        self.__config_manager = ConfigManager
        self.__config_path = Constants.CONFIG_FILES['CONFIG']

    def load_preferences_file(self):
        saved_prefs = {}
        if Path.is_file(self.__config_path):
            self.__config_manager.load_config(config=self.__config_path, saved_prefs=saved_prefs)

        config.update(filter(lambda i: i[0] in config, saved_prefs.items()))

        self.__config_manager.update_config_hash(config=config, module='preferences')

    def write_preferences_file(self):
        self.__config_manager.write_config(config=config, config_path=self.__config_path, module='preferences')


PreferenceManager = _PreferenceManager()
