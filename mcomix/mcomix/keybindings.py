# -*- coding: utf-8 -*-

""" Dynamic hotkey management

This module handles global hotkeys that were previously hardcoded in events.py.
All menu accelerators are handled using GTK's built-in accelerator map. The map
doesn't seem to support multiple keybindings for one action, though, so this
module takes care of the problem.

At runtime, other modules can register a callback for a specific action name.
This action name has to be registered in BINDING_INFO, or an Exception will be
thrown. The module can pass a list of default keybindings. If the user hasn't
configured different bindings, the default ones will be used.

Afterwards, the action will be stored together with its keycode/modifier in a
dictionary:
(keycode: int, modifier: GdkModifierType) =>
    (action: string, callback: func, args: list, kwargs: dict)

Default keybindings will be stored here at initialization:
action-name: string => [keycodes: list]


Each action_name can have multiple keybindings.
"""

import json
from collections import defaultdict

from gi.repository import Gtk

from mcomix import constants, log

#: Bindings defined in this dictionary will appear in the configuration dialog.
#: If 'group' is None, the binding cannot be modified from the preferences dialog.
BINDING_INFO = {
    # Navigation between pages, archives, directories
    'previous_page': {'title': 'Previous page', 'group': 'Navigation'},
    'next_page': {'title': 'Next page', 'group': 'Navigation'},
    'previous_page_ff': {'title': 'Back ten pages', 'group': 'Navigation'},
    'next_page_ff': {'title': 'Forward ten pages', 'group': 'Navigation'},
    'previous_page_dynamic': {'title': 'Previous page (dynamic)', 'group': 'Navigation'},
    'next_page_dynamic': {'title': 'Next page (dynamic)', 'group': 'Navigation'},
    'previous_page_singlestep': {'title': 'Previous page (always one page)', 'group': 'Navigation'},
    'next_page_singlestep': {'title': 'Next page (always one page)', 'group': 'Navigation'},

    'first_page': {'title': 'First page', 'group': 'Navigation'},
    'last_page': {'title': 'Last page', 'group': 'Navigation'},
    'go_to': {'title': 'Go to page', 'group': 'Navigation'},

    'next_archive': {'title': 'Next archive', 'group': 'Navigation'},
    'previous_archive': {'title': 'Previous archive', 'group': 'Navigation'},
    'next_directory': {'title': 'Next directory', 'group': 'Navigation'},
    'previous_directory': {'title': 'Previous directory', 'group': 'Navigation'},

    # Scrolling
    'scroll_left_bottom': {'title': 'Scroll to bottom left', 'group': 'Scroll'},
    'scroll_middle_bottom': {'title': 'Scroll to bottom center', 'group': 'Scroll'},
    'scroll_right_bottom': {'title': 'Scroll to bottom right', 'group': 'Scroll'},

    'scroll_left_middle': {'title': 'Scroll to middle left', 'group': 'Scroll'},
    'scroll_middle': {'title': 'Scroll to center', 'group': 'Scroll'},
    'scroll_right_middle': {'title': 'Scroll to middle right', 'group': 'Scroll'},

    'scroll_left_top': {'title': 'Scroll to top left', 'group': 'Scroll'},
    'scroll_middle_top': {'title': 'Scroll to top center', 'group': 'Scroll'},
    'scroll_right_top': {'title': 'Scroll to top right', 'group': 'Scroll'},

    'scroll_down': {'title': 'Scroll down', 'group': 'Scroll'},
    'scroll_up': {'title': 'Scroll up', 'group': 'Scroll'},
    'scroll_right': {'title': 'Scroll right', 'group': 'Scroll'},
    'scroll_left': {'title': 'Scroll left', 'group': 'Scroll'},

    'smart_scroll_up': {'title': 'Smart scroll up', 'group': 'Scroll'},
    'smart_scroll_down': {'title': 'Smart scroll down', 'group': 'Scroll'},

    # View
    'zoom_in': {'title': 'Zoom in', 'group': 'Zoom'},
    'zoom_out': {'title': 'Zoom out', 'group': 'Zoom'},
    'zoom_original': {'title': 'Normal size', 'group': 'Zoom'},

    'keep_transformation': {'title': 'Keep transformation', 'group': 'Transformation'},
    'rotate_90': {'title': 'Rotate 90 degrees CW', 'group': 'Transformation'},
    'rotate_180': {'title': 'Rotate 180 degrees', 'group': 'Transformation'},
    'rotate_270': {'title': 'Rotate 90 degrees CCW', 'group': 'Transformation'},
    'flip_horiz': {'title': 'Flip horizontally', 'group': 'Transformation'},
    'flip_vert': {'title': 'Flip vertically', 'group': 'Transformation'},
    'no_autorotation': {'title': 'Never autorotate', 'group': 'Transformation'},

    'rotate_90_width': {'title': 'Rotate 90 degrees CW', 'group': 'Autorotate by width'},
    'rotate_270_width': {'title': 'Rotate 90 degrees CCW', 'group': 'Autorotate by width'},
    'rotate_90_height': {'title': 'Rotate 90 degrees CW', 'group': 'Autorotate by height'},
    'rotate_270_height': {'title': 'Rotate 90 degrees CCW', 'group': 'Autorotate by height'},

    'double_page': {'title': 'Double page mode', 'group': 'View mode'},
    'manga_mode': {'title': 'Manga mode', 'group': 'View mode'},
    'invert_scroll': {'title': 'Invert smart scroll', 'group': 'View mode'},

    'lens': {'title': 'Magnifying lens', 'group': 'View mode'},
    'stretch': {'title': 'Stretch small images', 'group': 'View mode'},

    'best_fit_mode': {'title': 'Best fit mode', 'group': 'View mode'},
    'fit_width_mode': {'title': 'Fit width mode', 'group': 'View mode'},
    'fit_height_mode': {'title': 'Fit height mode', 'group': 'View mode'},
    'fit_size_mode': {'title': 'Fit size mode', 'group': 'View mode'},
    'fit_manual_mode': {'title': 'Manual zoom mode', 'group': 'View mode'},

    # General UI
    'exit_fullscreen': {'title': 'Exit from fullscreen', 'group': 'User interface'},

    'osd_panel': {'title': 'Show OSD panel', 'group': 'User interface'},
    'minimize': {'title': 'Minimize', 'group': 'User interface'},
    'fullscreen': {'title': 'Fullscreen', 'group': 'User interface'},
    'toolbar': {'title': 'Show/hide toolbar', 'group': 'User interface'},
    'menubar': {'title': 'Show/hide menubar', 'group': 'User interface'},
    'statusbar': {'title': 'Show/hide statusbar', 'group': 'User interface'},
    'scrollbar': {'title': 'Show/hide scrollbars', 'group': 'User interface'},
    'thumbnails': {'title': 'Thumbnails', 'group': 'User interface'},
    'hide_all': {'title': 'Show/hide all', 'group': 'User interface'},
    'slideshow': {'title': 'Start slideshow', 'group': 'User interface'},

    # File operations
    'move_file': {'title': 'Move to subdirectory', 'group': 'File'},
    'delete': {'title': 'Delete', 'group': 'File'},
    'refresh_archive': {'title': 'Refresh', 'group': 'File'},
    'close': {'title': 'Close', 'group': 'File'},
    'quit': {'title': 'Quit', 'group': 'File'},
    'save_and_quit': {'title': 'Save and quit', 'group': 'File'},
    'extract_page': {'title': 'Save As', 'group': 'File'},

    'comments': {'title': 'Archive comments', 'group': 'File'},
    'properties': {'title': 'Properties', 'group': 'File'},
    'preferences': {'title': 'Preferences', 'group': 'File'},

    'edit_archive': {'title': 'Edit archive', 'group': 'File'},
    'open': {'title': 'Open', 'group': 'File'},
    'enhance_image': {'title': 'Enhance image', 'group': 'File'},
    'library': {'title': 'Library', 'group': 'File'},
}

# Generate 9 entries for executing command 1 to 9
for i in range(1, 10):
    BINDING_INFO['execute_command_%d' % i] = {
        'title': 'Execute external command' + ' (%d)' % i,
        'group': 'External commands'
    }


class _KeybindingManager(object):
    def __init__(self, window):
        #: Main window instance
        self._window = window

        self._action_to_callback = {}  # action name => (func, args, kwargs)
        self._action_to_bindings = defaultdict(list)  # action name => [ (key code, key modifier), ]
        self._binding_to_action = {}  # (key code, key modifier) => action name

        self._initialize()

    def register(self, name, bindings, callback, args=[], kwargs={}):
        """ Registers an action for a predefined keybinding name.
        @param name: Action name, defined in L{BINDING_INFO}.
        @param bindings: List of keybinding strings, as understood
                         by L{Gtk.accelerator_parse}. Only used if no
                         bindings were loaded for this action.
        @param callback: Function callback
        @param args: List of arguments to pass to the callback
        @param kwargs: List of keyword arguments to pass to the callback.
        """
        assert name in BINDING_INFO, "'%s' isn't a valid keyboard action." % name

        # Load stored keybindings, or fall back to passed arguments
        keycodes = self._action_to_bindings[name]
        if not keycodes:
            keycodes = [Gtk.accelerator_parse(binding) for binding in bindings]

        for keycode in keycodes:
            if keycode in self._binding_to_action.keys():
                if self._binding_to_action[keycode] != name:
                    log.warning('Keybinding for "%(action)s" overrides hotkey for another action.',
                                {"action": name})
                    log.warning('Binding %s overrides %r', keycode, self._binding_to_action[keycode])
            else:
                self._binding_to_action[keycode] = name
                self._action_to_bindings[name].append(keycode)

        # Add gtk accelerator for labels in menu
        if len(self._action_to_bindings[name]) > 0:
            key, mod = self._action_to_bindings[name][0]
            Gtk.AccelMap.change_entry('<Actions>/mcomix-main/%s' % name, key, mod, True)

        self._action_to_callback[name] = (callback, args, kwargs)

    def edit_accel(self, name, new_binding, old_binding):
        """ Changes binding for an action
        @param name: Action name
        @param new_binding: Binding to be assigned to action
        @param old_binding: Binding to be removed from action [ can be empty: "" ]

        @return None: new_binding wasn't in any action
                action name: where new_binding was before
        """
        assert name in BINDING_INFO, "'%s' isn't a valid keyboard action." % name

        nb = Gtk.accelerator_parse(new_binding)
        old_action_with_nb = self._binding_to_action.get(nb)
        if old_action_with_nb is not None:
            # The new key is already bound to an action, erase the action
            self._binding_to_action.pop(nb)
            self._action_to_bindings[old_action_with_nb].remove(nb)

        if old_binding and name != old_action_with_nb:
            # The action already had a key that is now being replaced
            ob = Gtk.accelerator_parse(old_binding)
            self._binding_to_action[nb] = name

            # Remove action bound to the key.
            if ob in self._binding_to_action:
                self._binding_to_action.pop(ob)

            if ob in self._action_to_bindings[name]:
                idx = self._action_to_bindings[name].index(ob)
                self._action_to_bindings[name].pop(idx)
                self._action_to_bindings[name].insert(idx, nb)
        else:
            self._binding_to_action[nb] = name
            self._action_to_bindings[name].append(nb)

        self.save()
        return old_action_with_nb

    def clear_accel(self, name, binding):
        """ Remove binding for an action """
        assert name in BINDING_INFO, "'%s' isn't a valid keyboard action." % name

        ob = Gtk.accelerator_parse(binding)
        self._action_to_bindings[name].remove(ob)
        self._binding_to_action.pop(ob)

        self.save()

    def clear_all(self):
        """ Removes all keybindings. The changes are only persisted if
        save() is called afterwards. """
        self._action_to_callback = {}
        self._action_to_bindings = defaultdict(list)
        self._binding_to_action = {}

    def execute(self, keybinding):
        """ Executes an action that has been registered for the
        passed keyboard event. If no action is bound to the passed key, this
        method is a no-op. """
        if keybinding in self._binding_to_action:
            action = self._binding_to_action[keybinding]
            func, args, kwargs = self._action_to_callback[action]
            self._window.stop_emission_by_name('key_press_event')
            return func(*args, **kwargs)

        # Some keys enable additional modifiers (NumLock enables GDK_MOD2_MASK),
        # which prevent direct lookup simply by being pressed.
        # XXX: Looking up by key/modifier probably isn't the best implementation,
        # so limit possible states to begin with?
        for stored_binding, action in self._binding_to_action.items():
            stored_keycode, stored_flags = stored_binding
            if stored_keycode == keybinding[0] and stored_flags & keybinding[1]:
                func, args, kwargs = self._action_to_callback[action]
                self._window.stop_emission_by_name('key_press_event')
                return func(*args, **kwargs)

    def save(self):
        """ Stores the keybindings that have been set to disk. """
        # Collect keybindings for all registered actions
        action_to_keys = {}
        for action, bindings in self._action_to_bindings.items():
            if bindings is not None:
                action_to_keys[action] = [
                    Gtk.accelerator_name(keyval, modifiers) for
                    (keyval, modifiers) in bindings
                ]
        with open(constants.KEYBINDINGS_CONF_PATH, "w") as fp:
            json.dump(action_to_keys, fp, indent=2)

    def _initialize(self):
        """ Restore keybindings from disk. """
        try:
            with open(constants.KEYBINDINGS_CONF_PATH, "r") as fp:
                stored_action_bindings = json.load(fp)
        except Exception as e:
            log.error("Couldn't load keybindings: %s", e)
            stored_action_bindings = {}

        for action in BINDING_INFO.keys():
            if action in stored_action_bindings:
                bindings = [
                    Gtk.accelerator_parse(keyname)
                    for keyname in stored_action_bindings[action]]
                self._action_to_bindings[action] = bindings
                for binding in bindings:
                    self._binding_to_action[binding] = action
            else:
                self._action_to_bindings[action] = []

    def get_bindings_for_action(self, name):
        """ Returns a list of (keycode, modifier) for the action C{name}. """
        return self._action_to_bindings[name]


_manager = None


def keybinding_manager(window):
    """ Returns a singleton instance of the keybinding manager. """
    global _manager
    if _manager:
        return _manager
    else:
        _manager = _KeybindingManager(window)
        return _manager
