# -*- coding: utf-8 -*-

"""Dynamic hotkey management

This module handles global hotkeys that were previously hardcoded in events.py.
All menu accelerators are handled using GTK's built-in accelerator map. The map
doesn't seem to support multiple keybindings for one action, though, so this
module takes care of the problem.

At runtime, other modules can register a callback for a specific action name.
This action name has to be registered in keybindings_map.BINDING_INFO, or an Exception will be
thrown. The module can pass a list of default keybindings. If the user hasn't
configured different bindings, the default ones will be used.

Afterwards, the action will be stored together with its keycode/modifier in a
dictionary:
(keycode: int, modifier: GdkModifierType) => (action: string, callback: func, callback_kwargs: dict)

Default keybindings will be stored here at initialization:
action-name: string => [keycodes: list]

Each action_name can have multiple keybindings"""

from collections import defaultdict
from pathlib import Path
from typing import Callable

from gi.repository import Gtk
from loguru import logger

from mcomix.config_backend import ConfigBackend
from mcomix.enums.config_files import ConfigFiles


class KeybindingManager:
    __slots__ = ('__window', '__action_to_callback', '__action_to_bindings', '__binding_to_action',
                 '__stored_action_bindings', '__keybindings_map', '__config_manager', '__keybindings_path')

    def __init__(self, window):
        super().__init__()

        #: Main window instance
        self.__window = window

        # action name => (func, callback_kwargs)
        self.__action_to_callback = {}
        # action name => [ (key code, key modifier), ]
        self.__action_to_bindings = defaultdict(list)
        # (key code, key modifier) => action name
        self.__binding_to_action = {}

        self.__stored_action_bindings = {}

        self.__keybindings_map = self.__window.keybindings_map

        self.__config_manager = ConfigBackend
        self.__keybindings_path = ConfigFiles.KEYBINDINGS.value

        self.load_keybindings_file()

    def load_keybindings_default(self):
        """
        default keybindings set in keybindings_map.py
        """

        for action_name, action_data in self.__keybindings_map.items():
            self.__stored_action_bindings[action_name] = action_data.keybindings.keybindings

    def load_keybindings_file(self):
        if Path.is_file(self.__keybindings_path):
            self.__config_manager.load_config(config=self.__keybindings_path,
                                              saved_prefs=self.__stored_action_bindings)

            self.__config_manager.update_config_hash(config=self.__stored_action_bindings,
                                                     module='keybindings')
        else:
            # dont need to update config hash if missing input.conf
            self.load_keybindings_default()

        self.register_keybindings()

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

        self.__config_manager.write_config(config=action_to_keys,
                                           config_path=self.__keybindings_path,
                                           module='keybindings')

    def register_keybindings(self):
        """
        inits self.__binding_to_action and self.__action_to_bindings
        """

        for action in self.__keybindings_map.keys():
            if action in self.__stored_action_bindings:
                bindings = [
                    Gtk.accelerator_parse(keyname)
                    for keyname in self.__stored_action_bindings[action]
                ]
                self.__action_to_bindings[action] = bindings
                for binding in bindings:
                    self.__binding_to_action[binding] = action
            else:
                self.__action_to_bindings[action] = []

    def register(self, name: str, callback: Callable, callback_kwargs: dict = None):
        """
        Registers an action for a predefined keybinding name.

        :param name: Action name, defined in L{keybindings_map.BINDING_INFO}.
        :param callback: Function callback
        :param callback_kwargs: List of keyword arguments to pass to the callback
        """

        if callback_kwargs is None:
            callback_kwargs = {}

        for keycode in self.__action_to_bindings[name]:
            if keycode in self.__binding_to_action.keys():
                if self.__binding_to_action[keycode] != name:
                    logger.warning(f'Keybinding for \'{name}\' overrides hotkey for another action.\n'
                                   f'Binding \'{keycode}\' overrides \'{self.__binding_to_action[keycode]}\'')
            else:
                self.__binding_to_action[keycode] = name
                self.__action_to_bindings[name].append(keycode)

        self.__action_to_callback[name] = (callback, callback_kwargs)

    def edit_accel(self, name: str, new_binding: str, old_binding: str):
        """
        Changes binding for an action

        :param name: Action name
        :param new_binding: Binding to be assigned to action
        :param old_binding: Binding to be removed from action [ can be empty: "" ]
        :returns: None: new_binding wasn't in any action action name: where new_binding was before
        """

        nb = Gtk.accelerator_parse(new_binding)
        old_action_with_nb = self.__binding_to_action.get(nb)
        if old_action_with_nb is not None:
            # The new key is already bound to an action, erase the action
            self.__binding_to_action.pop(nb)
            self.__action_to_bindings[old_action_with_nb].remove(nb)

        if old_binding and name != old_action_with_nb:
            # The action already had a key that is now being replaced
            ob = Gtk.accelerator_parse(old_binding)
            self.__binding_to_action[nb] = name

            # Remove action bound to the key.
            if ob in self.__binding_to_action:
                self.__binding_to_action.pop(ob)

            if ob in self.__action_to_bindings[name]:
                idx = self.__action_to_bindings[name].index(ob)
                self.__action_to_bindings[name].pop(idx)
                self.__action_to_bindings[name].insert(idx, nb)
        else:
            self.__binding_to_action[nb] = name
            self.__action_to_bindings[name].append(nb)

        return old_action_with_nb

    def clear_accel(self, name: str, binding: str):
        """
        Remove binding for an action
        """

        ob = Gtk.accelerator_parse(binding)
        self.__action_to_bindings[name].remove(ob)
        self.__binding_to_action.pop(ob)

    def reset_keybindings(self):
        """
        Reset all keybindings. Changes will persisted since the keybinding
        hashes will no longer match
        """

        self.__action_to_callback = {}
        self.__action_to_bindings = defaultdict(list)
        self.__binding_to_action = {}
        self.__stored_action_bindings = {}

        self.load_keybindings_default()
        self.register_keybindings()

    def execute(self, keybinding: tuple):
        """
        Executes an action that has been registered for the
        passed keyboard event. If no action is bound to the passed key, this
        method is a no-op
        """

        if keybinding in self.__binding_to_action:
            action = self.__binding_to_action[keybinding]
            func, func_kwargs = self.__action_to_callback[action]
            self.__window.stop_emission_by_name('key_press_event')
            return func(**func_kwargs)

        # Some keys enable additional modifiers (NumLock enables GDK_MOD2_MASK),
        # which prevent direct lookup simply by being pressed.
        # XXX: Looking up by key/modifier probably isn't the best implementation,
        # so limit possible states to begin with?
        for stored_binding, action in self.__binding_to_action.items():
            stored_keycode, stored_flags = stored_binding
            if stored_keycode == keybinding[0] and stored_flags & keybinding[1]:
                func, func_kwargs = self.__action_to_callback[action]
                self.__window.stop_emission_by_name('key_press_event')
                return func(**func_kwargs)

    def get_bindings_for_action(self, name):
        """
        Returns a list of (keycode, modifier) for the action C{name}
        """

        return self.__action_to_bindings[name]
