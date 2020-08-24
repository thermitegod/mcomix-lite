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
(keycode: int, modifier: GdkModifierType) =>
    (action: string, callback: func, args: list, kwargs: dict)

Default keybindings will be stored here at initialization:
action-name: string => [keycodes: list]

Each action_name can have multiple keybindings"""

from collections import defaultdict
from pathlib import Path

from gi.repository import Gtk
from loguru import logger

from mcomix import constants, keybindings_map, config


class _KeybindingInterface:
    def __init__(self, window):
        super().__init__()

        #: Main window instance
        self.__window = window

        self.__action_to_callback = {}  # action name => (func, args, kwargs)
        self.__action_to_bindings = defaultdict(list)  # action name => [ (key code, key modifier), ]
        self.__binding_to_action = {}  # (key code, key modifier) => action name

        self.__keybindings_path = constants.KEYBINDINGS_PATH
        self.__keybindings_hash = {'sha256': None}

        self.load_keybindings_file()

    def register(self, name, callback, args=None, kwargs=None, bindings=None):
        """
        Registers an action for a predefined keybinding name.

        :param name: Action name, defined in L{keybindings_map.BINDING_INFO}.
        :param bindings: List of keybinding strings, as understood
                         by L{Gtk.accelerator_parse}. Only used if no
                         bindings were loaded for this action.
        :param callback: Function callback
        :param args: List of arguments to pass to the callback
        :param kwargs: List of keyword arguments to pass to the callback
        """

        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        if bindings is None:
            bindings = []

        assert name in keybindings_map.BINDING_INFO, f'"{name}" is not a valid keyboard action.'

        # Load stored keybindings, or fall back to passed arguments
        if not (keycodes := self.__action_to_bindings[name]):
            keycodes = [Gtk.accelerator_parse(binding) for binding in bindings]

        for keycode in keycodes:
            if keycode in self.__binding_to_action.keys():
                if self.__binding_to_action[keycode] != name:
                    logger.warning(f'Keybinding for \'{name}\' overrides hotkey for another action.\n'
                                   f'Binding \'{keycode}\' overrides \'{self.__binding_to_action[keycode]}\'')
            else:
                self.__binding_to_action[keycode] = name
                self.__action_to_bindings[name].append(keycode)

        # Add gtk accelerator for labels in menu
        if len(self.__action_to_bindings[name]) > 0:
            key, mod = self.__action_to_bindings[name][0]
            Gtk.AccelMap.change_entry(f'<Actions>/mcomix-main/{name}', key, mod, True)

        self.__action_to_callback[name] = (callback, args, kwargs)

    def edit_accel(self, name, new_binding, old_binding):
        """
        Changes binding for an action

        :param name: Action name
        :param new_binding: Binding to be assigned to action
        :param old_binding: Binding to be removed from action [ can be empty: "" ]
        :returns: None: new_binding wasn't in any action action name: where new_binding was before
        """

        assert name in keybindings_map.BINDING_INFO, f'"{name}" is not a valid keyboard action.'

        nb = Gtk.accelerator_parse(new_binding)
        if (old_action_with_nb := self.__binding_to_action.get(nb)) is not None:
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

    def clear_accel(self, name, binding):
        """
        Remove binding for an action
        """

        assert name in keybindings_map.BINDING_INFO, f'"{name}" is not a valid keyboard action.'

        ob = Gtk.accelerator_parse(binding)
        self.__action_to_bindings[name].remove(ob)
        self.__binding_to_action.pop(ob)

    def clear_all(self):
        """
        Removes all keybindings. The changes are only persisted if save() is called afterwards
        """

        self.__action_to_callback = {}
        self.__action_to_bindings = defaultdict(list)
        self.__binding_to_action = {}

    def execute(self, keybinding):
        """
        Executes an action that has been registered for the
        passed keyboard event. If no action is bound to the passed key, this
        method is a no-op
        """

        if keybinding in self.__binding_to_action:
            action = self.__binding_to_action[keybinding]
            func, args, kwargs = self.__action_to_callback[action]
            self.__window.stop_emission_by_name('key_press_event')
            return func(*args, **kwargs)

        # Some keys enable additional modifiers (NumLock enables GDK_MOD2_MASK),
        # which prevent direct lookup simply by being pressed.
        # XXX: Looking up by key/modifier probably isn't the best implementation,
        # so limit possible states to begin with?
        for stored_binding, action in self.__binding_to_action.items():
            stored_keycode, stored_flags = stored_binding
            if stored_keycode == keybinding[0] and stored_flags & keybinding[1]:
                func, args, kwargs = self.__action_to_callback[action]
                self.__window.stop_emission_by_name('key_press_event')
                return func(*args, **kwargs)

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

        sha256hash = config.ConfigManager.hash_config(action_to_keys)
        if sha256hash == self.__keybindings_hash['sha256']:
            logger.info('No changes to write for keybindings')
            return
        self.__keybindings_hash['sha256'] = sha256hash

        logger.info('Writing changes to keybindings')

        config.ConfigManager.write_config(action_to_keys, self.__keybindings_path)

    def load_keybindings_file(self):
        stored_action_bindings = {}
        if Path.is_file(self.__keybindings_path):
            config.ConfigManager.load_config(self.__keybindings_path, stored_action_bindings)
        else:
            stored_action_bindings = keybindings_map.DEFAULT_BINDINGS.copy()

        for action in keybindings_map.BINDING_INFO.keys():
            if action in stored_action_bindings:
                bindings = [
                    Gtk.accelerator_parse(keyname)
                    for keyname in stored_action_bindings[action]]
                self.__action_to_bindings[action] = bindings
                for binding in bindings:
                    self.__binding_to_action[binding] = action
            else:
                self.__action_to_bindings[action] = []

        self.__keybindings_hash['sha256'] = config.ConfigManager.hash_config(stored_action_bindings)

    def get_bindings_for_action(self, name):
        """
        Returns a list of (keycode, modifier) for the action C{name}
        """

        return self.__action_to_bindings[name]


class _KeybindingManager:
    def __init__(self):
        super().__init__()

        self.__manager = None

    def keybinding_manager(self, window):
        if self.__manager is None:
            self.__manager = _KeybindingInterface(window)
        return self.__manager


# Singleton instance
KeybindingManager = _KeybindingManager()



