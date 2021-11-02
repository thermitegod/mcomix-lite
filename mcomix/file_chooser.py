# -*- coding: utf-8 -*-

"""filechooser_chooser.py - Custom FileChooserDialog implementations"""

import fnmatch
from pathlib import Path

from gi.repository import Gtk

from mcomix.formats.archive import ArchiveSupported
from mcomix.formats.image import ImageSupported
from mcomix.preferences import config


class FileChooser(Gtk.Dialog):
    """
    We roll our own FileChooserDialog because the one in GTK seems
    buggy with the preview widget. The <action> argument dictates what type
    of filechooser dialog we want (i.e. it is Gtk.FileChooserAction.OPEN
    or Gtk.FileChooserAction.SAVE).
    """

    __slots__ = ('__window', '__action', '__last_activated_file', '__filechooser')

    def __init__(self, window):
        self.__window = window
        self.__action = Gtk.FileChooserAction.OPEN
        self.__last_activated_file = None

        super().__init__(title='Open')

        self.set_modal(True)
        self.set_transient_for(self.__window)
        self.add_buttons(*(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.set_default_response(Gtk.ResponseType.OK)

        self.__filechooser = Gtk.FileChooserWidget(action=self.__action)
        self.__filechooser.set_select_multiple(True)
        self.__filechooser.set_size_request(1280, 720)
        self.vbox.pack_start(self.__filechooser, True, True, 0)
        self.set_border_width(4)
        self.__filechooser.set_border_width(6)
        self.connect('response', self._response)
        self.__filechooser.connect('file_activated', self._response, Gtk.ResponseType.OK)

        self.add_filter('All files', [])
        self.add_archive_filters()
        self.add_image_filters()

        filters = self.__filechooser.list_filters()
        self.__filechooser.set_filter(filters[config['FILECHOOSER_LAST_FILTER']])

        try:
            current_file = self.__window.filehandler.get_path_to_base()
            if current_file is not None:
                # If a file is currently open, use its path
                self.__filechooser.set_current_folder(str(current_file.parent))
            elif self.__last_activated_file:
                # If no file is open, use the last stored file
                self.__filechooser.set_filename(self.__last_activated_file)
            else:
                # If no file was stored yet, fall back to preferences
                self.__filechooser.set_current_folder(config['FILECHOOSER_LAST_BROWSED_PATH'])
        except TypeError:
            self.__filechooser.set_current_folder(str(Path.home()))

        self.show_all()

    def add_filter(self, name, patterns=None):
        """
        Add a filter, called <name>, for each mime type in <mimes> and
        each pattern in <patterns> to the filechooser
        """

        if patterns is None:
            patterns = []

        ffilter = Gtk.FileFilter()
        ffilter.add_custom(Gtk.FileFilterFlags.FILENAME | Gtk.FileFilterFlags.MIME_TYPE,
                           self._filter, patterns)

        ffilter.set_name(name)
        self.__filechooser.add_filter(ffilter)
        return ffilter

    def add_archive_filters(self):
        """
        Add archive filters to the filechooser
        """

        ffilter = Gtk.FileFilter()
        ffilter.set_name('All archives')
        self.__filechooser.add_filter(ffilter)

        for ext in ArchiveSupported.EXTS.value:
            ffilter.add_pattern(f'*{ext}')

    def add_image_filters(self):
        """
        Add images filters to the filechooser
        """

        ffilter = Gtk.FileFilter()
        ffilter.set_name('All images')
        self.__filechooser.add_filter(ffilter)

        for ext in ImageSupported.EXTS.value:
            ffilter.add_pattern(f'*{ext}')

    def files_chosen(self, paths: list):
        if paths:
            filter_index = self.__filechooser.list_filters().index(self.__filechooser.get_filter())
            config['FILECHOOSER_LAST_FILTER'] = filter_index

            files = [Path(path) for path in paths]
            self.__window.filehandler.initialize_fileprovider(files)
            self.__window.filehandler.open_file(Path(files[0]))

        self.destroy()

    def _filter(self, filter_info, pattern):
        """
        Callback function used to determine if a file
        should be filtered or not. Returns True
        if the file passed in C{filter_info} should be displayed
        """

        return bool(filter(lambda match_pattern: fnmatch.fnmatch(filter_info.filename, match_pattern), pattern))

    def _response(self, widget, response):
        """
        Return a list of the paths of the chosen files, or None if the
        event only changed the current directory
        """

        if not response == Gtk.ResponseType.OK:
            self.files_chosen([])
            return

        filenames = self.__filechooser.get_filenames()
        if not filenames:
            return

        paths = [path for path in filenames if Path.is_file(Path(path))]

        self.__last_activated_file = paths[0]
        self.files_chosen(paths)

        config['FILECHOOSER_LAST_BROWSED_PATH'] = self.__filechooser.get_current_folder()
