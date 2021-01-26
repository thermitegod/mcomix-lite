# -*- coding: utf-8 -*-

from collections import defaultdict
from pathlib import Path

from gi.repository import Gtk

from mcomix.config_backend import ConfigBackend
from mcomix.constants import Constants
from mcomix.keybindings_map import KeyBindingsMap


class KeybindingConfig:
    def __init__(self):
        super().__init__()

        # action name => [ (key code, key modifier), ]
        self.__action_to_bindings = defaultdict(list)
        # (key code, key modifier) => action name
        self.__binding_to_action = {}

        self.__config_manager = ConfigBackend
        self.__keybindings_path = Constants.CONFIG_FILES['KEYBINDINGS']

    @property
    def action_to_bindings(self):
        return self.__action_to_bindings

    @property
    def binding_to_action(self):
        return self.__binding_to_action

    def load_keybindings_file(self):
        stored_action_bindings = {}
        if Path.is_file(self.__keybindings_path):
            self.__config_manager.load_config(config=self.__keybindings_path, saved_prefs=stored_action_bindings)
        else:
            for action_name, action_data in KeyBindingsMap.BINDINGS.items():
                stored_action_bindings[action_name] = action_data.keybindings

        for action in KeyBindingsMap.BINDINGS.keys():
            if action in stored_action_bindings:
                bindings = [
                    Gtk.accelerator_parse(keyname)
                    for keyname in stored_action_bindings[action]]
                self.__action_to_bindings[action] = bindings
                for binding in bindings:
                    self.__binding_to_action[binding] = action
            else:
                self.__action_to_bindings[action] = []

        self.__config_manager.update_config_hash(config=stored_action_bindings, module='keybindings')

    def write_keybindings_file(self):
        """
        Stores the keybindings that have been set to disk
        """

        # Collect keybindings for all registered actions
        action_to_keys = {}
        for action, bindings in self.__action_to_bindings.items():
            if bindings is not None:
                action_to_keys[action] = [
                    Gtk.accelerator_name(keyval, modifiers) for
                    (keyval, modifiers) in bindings
                ]

        self.__config_manager.write_config(config=action_to_keys, config_path=self.__keybindings_path,
                                           module='keybindings')
