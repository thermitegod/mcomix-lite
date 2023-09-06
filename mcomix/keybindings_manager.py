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

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from gi.repository import Gtk

from mcomix.config_backend import ConfigBackend
from mcomix.enums import ConfigFiles, ConfigType
from mcomix.keybindings_map import KeyBindingsMap

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class KeybindingManager:
    def __init__(self, window: MainWindow):
        super().__init__()

        #: Main window instance
        self.__window = window

        # action name => (event, event_type, event_kwargs)
        self.__action_to_callback = {}
        # action name => [ (key code, key modifier), ]
        self.__action_to_bindings = defaultdict(list)
        # (key code, key modifier) => action name
        self.__binding_to_action = {}

        self.__stored_action_bindings = {}

        self.__keybindings_map = KeyBindingsMap().bindings

        self.__config_manager = ConfigBackend
        self.__keybindings_path = ConfigFiles.KEYBINDINGS.value

        self._load_keybindings_file()
        self._register_keybindings()

    def _load_keybindings_default(self):
        """
        default keybindings set in keybindings_map.py
        """

        for action_name, action_data in self.__keybindings_map.items():
            self.__stored_action_bindings[action_name] = action_data.keybindings.keybindings

    def _load_keybindings_file(self):
        if Path.is_file(self.__keybindings_path):
            self.__config_manager.load_config(config=self.__keybindings_path,
                                              saved_prefs=self.__stored_action_bindings)

            self.__config_manager.update_config_hash(config=self.__stored_action_bindings,
                                                     module=ConfigType.KEYBINDINGS)
        else:
            # dont need to update config hash if missing input.conf
            self._load_keybindings_default()

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
                                           module=ConfigType.KEYBINDINGS)

    def _register_keybindings(self):
        for action_name, action_data in self.__keybindings_map.items():
            self._register_keybindings_structure(action_name)
            self._register_keybindings_events(action_name, action_data)

    def _register_keybindings_structure(self, action_name):
        """
        inits self.__binding_to_action and self.__action_to_bindings
        """

        if not action_name in self.__stored_action_bindings:
            self.__action_to_bindings[action_name] = []
            return

        bindings = [
            Gtk.accelerator_parse(keyname)
            for keyname in self.__stored_action_bindings[action_name]
        ]
        self.__action_to_bindings[action_name] = bindings
        for binding in bindings:
            self.__binding_to_action[binding] = action_name

    def _register_keybindings_events(self, action_name, action_data):
        """
        Registers keyboard events and their default binings, and hooks
        them up with their respective callback functions
        """

        event=action_data.key_event.event
        event_type=action_data.key_event.event_type
        event_kwargs=action_data.key_event.event_kwargs

        if event_kwargs is None:
            event_kwargs = {}

        for keycode in self.__action_to_bindings[action_name]:
            if keycode in self.__binding_to_action:
                continue

            self.__binding_to_action[keycode] = action_name
            self.__action_to_bindings[action_name].append(keycode)

        self.__action_to_callback[action_name] = (event, event_type, event_kwargs)

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

        self._load_keybindings_default()
        self._register_keybindings()

    def execute(self, keybinding: tuple):
        """
        Executes an action that has been registered for the
        passed keyboard event. If no action is bound to the passed key, this
        method is a no-op
        """

        if keybinding in self.__binding_to_action:
            action = self.__binding_to_action[keybinding]
            func, event_type, func_kwargs = self.__action_to_callback[action]
            self.__window.stop_emission_by_name('key_press_event')
            return func(event_type, func_kwargs)

        # Some keys enable additional modifiers (NumLock enables GDK_MOD2_MASK),
        # which prevent direct lookup simply by being pressed.
        # XXX: Looking up by key/modifier probably isn't the best implementation,
        # so limit possible states to begin with?
        for stored_binding, action in self.__binding_to_action.items():
            stored_keycode, stored_flags = stored_binding
            if stored_keycode == keybinding[0] and stored_flags & keybinding[1]:
                func, event_type, func_kwargs = self.__action_to_callback[action]
                self.__window.stop_emission_by_name('key_press_event')
                return func(event_type, func_kwargs)

    def get_bindings_for_action(self, name):
        """
        Returns a list of (keycode, modifier) for the action C{name}
        """

        return self.__action_to_bindings[name]
