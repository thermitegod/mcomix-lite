# -*- coding: utf-8 -*-

"""Configuration tree view for the preferences dialog to edit keybindings"""

from gi.repository import Gtk


class KeybindingEditorWindow(Gtk.ScrolledWindow):
    __slots__ = ('__window', '__keybindings', '__keybindings_map',
                 '__accel_column_num', '__action_treeiter_map')

    def __init__(self, window):
        """
        :param keymanager: KeybindingManager instance
        """

        super().__init__()

        self.set_border_width(5)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)

        self.__window = window
        self.__keybindings = self.__window.keybindings
        self.__keybindings_map = self.__window.keybindings_map

        # max number of keybindings for a single action
        self.__accel_column_num = 5

        # Human name, action name, true value, shortcut 1, shortcut 2, ...
        model = [str, str, 'gboolean']
        model.extend([str, ] * self.__accel_column_num)

        treestore = self.__treestore = Gtk.TreeStore(*model)
        self.refresh_model()

        treeview = Gtk.TreeView(model=treestore)

        tvcol1 = Gtk.TreeViewColumn('Name')
        treeview.append_column(tvcol1)
        cell1 = Gtk.CellRendererText()
        tvcol1.pack_start(cell1, True)
        tvcol1.set_attributes(cell1, text=0, editable=2)

        for idx in range(self.__accel_column_num):
            tvc = Gtk.TreeViewColumn(f'Key {idx + 1}')
            treeview.append_column(tvc)
            accel_cell = Gtk.CellRendererAccel()
            accel_cell.connect('accel-edited', self._get_on_accel_edited(idx))
            accel_cell.connect('accel-cleared', self._get_on_accel_cleared(idx))
            tvc.pack_start(accel_cell, True)
            tvc.add_attribute(accel_cell, 'text', 3 + idx)
            tvc.add_attribute(accel_cell, 'editable', 2)

        # Allow sorting on the column
        tvcol1.set_sort_column_id(0)

        self.add(treeview)

        self.__action_treeiter_map = {}

    def refresh_model(self):
        """
        Initializes the model from data provided by the keybinding manager
        """

        self.__treestore.clear()
        section_order = list(set(d.info.group for d in self.__keybindings_map.values()))
        section_order.sort()
        section_parent_map = {}
        for section_name in section_order:
            row = [section_name, None, False]
            row.extend([None, ] * self.__accel_column_num)
            section_parent_map[section_name] = self.__treestore.append(None, row)

        action_treeiter_map = self.__action_treeiter_map = {}

        for action_name, action_data in self.__keybindings_map.items():
            title = action_data.info.title
            group_name = action_data.info.group
            old_bindings = self.__keybindings.get_bindings_for_action(action_name)
            acc_list = ['', ] * self.__accel_column_num
            for idx in range(self.__accel_column_num):
                if len(old_bindings) > idx:
                    acc_list[idx] = Gtk.accelerator_name(*old_bindings[idx])

            row = [title, action_name, True]
            row.extend(acc_list)
            treeiter = self.__treestore.append(section_parent_map[group_name], row)
            action_treeiter_map[action_name] = treeiter

    def _get_on_accel_edited(self, column: int):
        def _on_accel_edited(renderer, path: str, accel_key: int, accel_mods, hardware_keycode: int):
            _iter = self.__treestore.get_iter(path)
            col = column + 3  # accel cells start from 3 position
            old_accel = self.__treestore.get(_iter, col)[0]
            new_accel = Gtk.accelerator_name(accel_key, accel_mods)
            self.__treestore.set_value(_iter, col, new_accel)
            action_name = self.__treestore.get_value(_iter, 1)
            affected_action = self.__keybindings.edit_accel(action_name, new_accel, old_accel)

            # Find affected row and cell
            if affected_action == action_name:
                for idx in range(self.__accel_column_num):
                    if idx != column and self.__treestore.get(_iter, idx + 3)[0] == new_accel:
                        self.__treestore.set_value(_iter, idx + 3, '')
            elif affected_action is not None:
                titer = self.__action_treeiter_map[affected_action]
                for idx in range(self.__accel_column_num):
                    if self.__treestore.get(titer, idx + 3)[0] == new_accel:
                        self.__treestore.set_value(titer, idx + 3, '')

            # updating gtk accelerator for label in menu
            if self.__keybindings.get_bindings_for_action(action_name)[0] == (accel_key, accel_mods):
                Gtk.AccelMap.change_entry(f'<Actions>/mcomix-master/{action_name}', accel_key, accel_mods, True)

        return _on_accel_edited

    def _get_on_accel_cleared(self, column: int):
        def _on_accel_cleared(renderer, path: str, *args):
            _iter = self.__treestore.get_iter(path)
            col = column + 3
            accel = self.__treestore.get(_iter, col)[0]
            action_name = self.__treestore.get_value(_iter, 1)
            if accel != '':
                self.__keybindings.clear_accel(action_name, accel)

                # updating gtk accelerator for label in menu
                if not self.__keybindings.get_bindings_for_action(action_name):
                    Gtk.AccelMap.change_entry(f'<Actions>/mcomix-master/{action_name}, 0, 0, True')
                else:
                    key, mods = self.__keybindings.get_bindings_for_action(action_name)[0]
                    Gtk.AccelMap.change_entry(f'<Actions>/mcomix-master/{action_name}', key, mods, True)

            self.__treestore.set_value(_iter, col, "")

        return _on_accel_cleared
