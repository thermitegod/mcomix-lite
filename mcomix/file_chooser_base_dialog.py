# -*- coding: utf-8 -*-

"""filechooser_chooser_base_dialog.py - Custom FileChooserDialog implementations"""

import fnmatch
import mimetypes
import os

from gi.repository import Gtk, Pango
from loguru import logger

from mcomix import archive_tools, constants, file_provider, image_tools, labels, message_dialog, thumbnail_tools, tools
from mcomix.preferences import prefs

mimetypes.init()


class BaseFileChooserDialog(Gtk.Dialog):
    """We roll our own FileChooserDialog because the one in GTK seems
    buggy with the preview widget. The <action> argument dictates what type
    of filechooser dialog we want (i.e. it is Gtk.FileChooserAction.OPEN
    or Gtk.FileChooserAction.SAVE).

    This is a base class for the _MainFileChooserDialog and SimpleFileChooserDialog.

    Subclasses should implement a method files_chosen(paths) that will be
    called once the filechooser has done its job and selected some files.
    If the dialog was closed or Cancel was pressed, <paths> is the empty list"""

    def __init__(self, parent, action=Gtk.FileChooserAction.OPEN):
        self.__action = action
        self.__destroyed = False
        self.__last_activated_file = None

        if action == Gtk.FileChooserAction.OPEN:
            title = 'Open'
            buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        else:
            title = 'Save'
            buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)

        super(BaseFileChooserDialog, self).__init__(title=title)
        self.set_transient_for(parent)
        self.add_buttons(*buttons)
        self.set_default_response(Gtk.ResponseType.OK)

        self.filechooser = Gtk.FileChooserWidget(action=action)
        self.filechooser.set_size_request(680, 420)
        self.vbox.pack_start(self.filechooser, True, True, 0)
        self.set_border_width(4)
        self.filechooser.set_border_width(6)
        self.connect('response', self._response)
        self.filechooser.connect('file_activated', self._response, Gtk.ResponseType.OK)

        preview_box = Gtk.VBox(homogeneous=False, spacing=10)
        preview_box.set_size_request(130, 0)
        self.__preview_image = Gtk.Image()
        self.__preview_image.set_size_request(130, 130)
        preview_box.pack_start(self.__preview_image, False, False, 0)
        self.filechooser.set_preview_widget(preview_box)

        pango_scale_small = (1 / 1.2)

        self.__namelabel = labels.FormattedLabel(weight=Pango.Weight.BOLD, scale=pango_scale_small)
        self.__namelabel.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        preview_box.pack_start(self.__namelabel, False, False, 0)

        self.__sizelabel = labels.FormattedLabel(scale=pango_scale_small)
        self.__sizelabel.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        preview_box.pack_start(self.__sizelabel, False, False, 0)
        self.filechooser.set_use_preview_label(False)
        preview_box.show_all()
        self.filechooser.connect('update-preview', self._update_preview)

        self.__all_files_filter = self.add_filter('All files', [], ['*'])

        try:
            # If a file is currently open, use its path
            if (current_file := self._current_file()) and os.path.exists(current_file):
                self.filechooser.set_current_folder(os.path.dirname(current_file))
            # If no file is open, use the last stored file
            elif (last_file := self.__last_activated_file) and os.path.exists(last_file):
                self.filechooser.set_filename(last_file)
            # If no file was stored yet, fall back to preferences
            elif os.path.isdir(prefs['path of last browsed in filechooser']):
                self.filechooser.set_current_folder(constants.HOME_DIR)
        except Exception:
            logger.error('probably broken prefs values')

        self.show_all()

    def add_filter(self, name, mimes, patterns=None):
        """Add a filter, called <name>, for each mime type in <mimes> and
        each pattern in <patterns> to the filechooser"""
        if patterns is None:
            patterns = []

        ffilter = Gtk.FileFilter()
        ffilter.add_custom(Gtk.FileFilterFlags.FILENAME | Gtk.FileFilterFlags.MIME_TYPE,
                           self._filter, (patterns, mimes))

        ffilter.set_name(name)
        self.filechooser.add_filter(ffilter)
        return ffilter

    def add_archive_filters(self):
        """Add archive filters to the filechooser"""
        ffilter = Gtk.FileFilter()
        ffilter.set_name('All archives')
        self.filechooser.add_filter(ffilter)
        for name in sorted(supported_formats := archive_tools.get_supported_formats()):
            mime_types, extensions = supported_formats[name]
            patterns = [f'*{ext}' for ext in extensions]
            self.add_filter(f'{name} archives', mime_types, patterns)
            for mime in mime_types:
                ffilter.add_mime_type(mime)
            for pat in patterns:
                ffilter.add_pattern(pat)

    def add_image_filters(self):
        """Add images filters to the filechooser"""
        ffilter = Gtk.FileFilter()
        ffilter.set_name('All images')
        self.filechooser.add_filter(ffilter)
        for name in sorted(supported_formats := image_tools.get_supported_formats()):
            mime_types, extensions = supported_formats[name]
            patterns = [f'*{ext}' for ext in extensions]
            self.add_filter(f'{name} images', mime_types, patterns)
            for mime in mime_types:
                ffilter.add_mime_type(mime)
            for pat in patterns:
                ffilter.add_pattern(pat)

    @staticmethod
    def _filter(filter_info, data):
        """Callback function used to determine if a file
        should be filtered or not. C{data} is a tuple containing
        (patterns, mimes) that should pass the test. Returns True
        if the file passed in C{filter_info} should be displayed"""
        match_patterns, match_mimes = data

        matches_mime = bool(filter(lambda match_mime:
                                   match_mime == filter_info.mime_type, match_mimes))
        matches_pattern = bool(filter(lambda match_pattern:
                                      fnmatch.fnmatch(filter_info.filename, match_pattern), match_patterns))

        return matches_mime or matches_pattern

    def collect_files_from_subdir(self, path, filter, recursive=False):
        """Finds archives within C{path} that match the L{Gtk.FileFilter} passed in C{filter}"""
        for dirpath, subdirs, files in os.scandir(path):
            for file in files:
                full_path = os.path.join(dirpath, file)
                mimetype = mimetypes.guess_type(full_path)[0] or 'application/octet-stream'
                filter_info = Gtk.FileFilterInfo()
                filter_info.contains = Gtk.FileFilterFlags.FILENAME | Gtk.FileFilterFlags.MIME_TYPE
                filter_info.filename = full_path
                filter_info.mime_type = mimetype

                if filter == self.__all_files_filter or filter.filter(filter_info):
                    yield full_path

            if not recursive:
                break

    @staticmethod
    def should_open_recursive():
        return False

    def _response(self, widget, response):
        """Return a list of the paths of the chosen files, or None if the
        event only changed the current directory"""
        if response == Gtk.ResponseType.OK:
            if not self.filechooser.get_filenames():
                return

            # Collect files, if necessary also from subdirectories
            filter = self.filechooser.get_filter()
            paths = []
            for path in self.filechooser.get_filenames():
                if os.path.isdir(path):
                    subdir_files = list(self.collect_files_from_subdir(path, filter, self.should_open_recursive()))
                    file_provider.FileProvider.sort_files(subdir_files)
                    paths.extend(subdir_files)
                else:
                    paths.append(path)

            # FileChooser.set_do_overwrite_confirmation() doesn't seem to
            # work on our custom dialog, so we use a simple alternative.
            first_path = self.filechooser.get_filenames()[0]
            if (self.__action == Gtk.FileChooserAction.SAVE and
                    not os.path.isdir(first_path) and
                    os.path.exists(first_path)):
                overwrite_dialog = message_dialog.MessageDialog(
                        self,
                        flags=0,
                        message_type=Gtk.MessageType.QUESTION,
                        buttons=Gtk.ButtonsType.OK_CANCEL)
                overwrite_dialog.set_text(f'A file named "{os.path.basename(first_path)}" '
                                          'already exists. Do you want to replace it?')

                if overwrite_dialog.run() != Gtk.ResponseType.OK:
                    self.stop_emission_by_name('response')
                    return

            self.__last_activated_file = first_path
            self.files_chosen(paths)

        else:
            self.files_chosen([])

        self.__destroyed = True

    def _update_preview(self, *args):
        if (path := self.filechooser.get_preview_filename()) and os.path.isfile(path):
            thumbnailer = thumbnail_tools.Thumbnailer(size=(128, 128))
            thumbnailer.thumbnail_finished += self._preview_thumbnail_finished
            thumbnailer.thumbnail(path, mt=True)
        else:
            self.__preview_image.clear()
            self.__namelabel.set_text('')
            self.__sizelabel.set_text('')

    def _preview_thumbnail_finished(self, filepath, pixbuf):
        """Called when the thumbnailer has finished creating the thumbnail for <filepath>"""
        if self.__destroyed:
            return

        if (current_path := self.filechooser.get_preview_filename()) and current_path == filepath:
            if pixbuf is None:
                self.__preview_image.clear()
                self.__namelabel.set_text('')
                self.__sizelabel.set_text('')

            else:
                pixbuf = image_tools.add_border(pixbuf, 1)
                self.__preview_image.set_from_pixbuf(pixbuf)
                self.__namelabel.set_text(os.path.basename(filepath))
                self.__sizelabel.set_text(tools.format_byte_size(os.stat(filepath).st_size))

    @staticmethod
    def _current_file():
        # XXX: This method defers the import of main to avoid cyclic imports during startup.
        from mcomix import main
        return main.main_window().filehandler.get_path_to_base()
