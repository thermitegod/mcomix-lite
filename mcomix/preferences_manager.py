# must not depend on GTK, PIL, or any other optional libraries.

from pathlib import Path

from mcomix.config_backend import ConfigBackend, ConfigType
from mcomix.enums import ConfigFiles
from mcomix.preferences import config


class PreferenceManager:
    def __init__(self):
        super().__init__()

        self.__config_manager = ConfigBackend
        self.__config_path = ConfigFiles.CONFIG.value

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
