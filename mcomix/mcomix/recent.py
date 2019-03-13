# -*- coding: utf-8 -*-

"""recent.py - Recent files handler."""

import glib
from gi.repository import GObject, Gtk
from urllib.request import pathname2url, url2pathname

from mcomix import archive_tools, image_tools, log, preferences


class RecentFilesMenu(Gtk.RecentChooserMenu):

    def __init__(self, ui, window):
        super(RecentFilesMenu, self).__init__()
        self._window = window
        self._manager = Gtk.RecentManager.get_default()

        self.set_sort_type(Gtk.RecentSortType.MRU)
        self.set_show_tips(True)

        rfilter = Gtk.RecentFilter()
        supported_formats = {}
        supported_formats.update(image_tools.get_supported_formats())
        supported_formats.update(archive_tools.get_supported_formats())
        for name in sorted(supported_formats):
            mime_types, extensions = supported_formats[name]
            patterns = ['*' + ext for ext in extensions]
            for mime in mime_types:
                rfilter.add_mime_type(mime)
            for pat in patterns:
                rfilter.add_pattern(pat)
        self.add_filter(rfilter)

        self.connect('item_activated', self._load)

    def _load(self, *args):
        uri = self.get_current_uri()
        path = url2pathname(uri[7:])
        did_file_load = self._window.filehandler.open_file(path)

        if not did_file_load:
            self.remove(path)

    def count(self):
        """ Returns the amount of stored entries. """
        return len(self._manager.get_items())

    def add(self, path):
        if not preferences.prefs['store recent file info']:
            return
        uri = ('file://' + pathname2url(path))
        self._manager.add_item(uri)

    def remove(self, path):
        if not preferences.prefs['store recent file info']:
            return
        uri = ('file://' + pathname2url(path))
        try:
            self._manager.remove_item(uri)
        except glib.GError:
            # Could not remove item
            pass

    def remove_all(self):
        """ Removes all entries to recently opened files. """
        try:
            self._manager.purge_items()
        except GObject.GError as error:
            log.debug(error)
