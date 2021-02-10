# -*- coding: utf-8 -*-

"""filechooser_chooser_base_dialog.py - Custom FileChooserDialog implementations"""

import fnmatch
from pathlib import Path

from gi.repository import Gtk
from loguru import logger

from mcomix.archive_tools import ArchiveTools
from mcomix.file_size import FileSize
from mcomix.image_tools import ImageTools
from mcomix.preferences import config
from mcomix.thumbnail_tools import Thumbnailer


class BaseFileChooserDialog(Gtk.Dialog):
    """
    We roll our own FileChooserDialog because the one in GTK seems
    buggy with the preview widget. The <action> argument dictates what type
    of filechooser dialog we want (i.e. it is Gtk.FileChooserAction.OPEN
    or Gtk.FileChooserAction.SAVE).

    Subclasses should implement a method files_chosen(paths) that will be
    called once the filechooser has done its job and selected some files.
    If the dialog was closed or Cancel was pressed, <paths> is the empty list
    """

    def __init__(self, parent):
        self.__action = Gtk.FileChooserAction.OPEN
        self.__destroyed = False
        self.__last_activated_file = None

        super().__init__(title='Open')

        self.set_transient_for(parent)
        self.add_buttons(*(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.set_default_response(Gtk.ResponseType.OK)

        self.filechooser = Gtk.FileChooserWidget(action=self.__action)
        self.filechooser.set_size_request(1280, 720)
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

        self.__namelabel = Gtk.Label()
        preview_box.pack_start(self.__namelabel, False, False, 0)

        self.__sizelabel = Gtk.Label()
        preview_box.pack_start(self.__sizelabel, False, False, 0)

        self.filechooser.set_use_preview_label(False)
        preview_box.show_all()
        self.filechooser.connect('update-preview', self._update_preview)

        self.__all_files_filter = self.add_filter('All files', [])

        try:
            current_file = self._current_file()
            if current_file:
                # If a file is currently open, use its path
                self.filechooser.set_current_folder(Path(current_file).parent)
            elif self.__last_activated_file:
                # If no file is open, use the last stored file
                self.filechooser.set_filename(self.__last_activated_file)
            else:
                # If no file was stored yet, fall back to preferences
                self.filechooser.set_current_folder(config['FILECHOOSER_LAST_BROWSED_PATH'])
        except Exception:
            logger.error('probably broken prefs values')

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
        self.filechooser.add_filter(ffilter)
        return ffilter

    def add_archive_filters(self):
        """
        Add archive filters to the filechooser
        """

        ffilter = Gtk.FileFilter()
        ffilter.set_name('All archives')
        self.filechooser.add_filter(ffilter)

        for ext in ArchiveTools.supported_archive_ext:
            ffilter.add_pattern(f'*{ext}')

    def add_image_filters(self):
        """
        Add images filters to the filechooser
        """

        ffilter = Gtk.FileFilter()
        ffilter.set_name('All images')
        self.filechooser.add_filter(ffilter)

        for ext in ImageTools.supported_image_exts:
            ffilter.add_pattern(f'*{ext}')

    @staticmethod
    def _filter(filter_info, pattern):
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

        if response == Gtk.ResponseType.OK:
            if not self.filechooser.get_filenames():
                return

            # Collect files, if necessary also from subdirectories
            paths = []
            for path in self.filechooser.get_filenames():
                if Path.is_dir(Path(path)):
                    for file in Path(path).iterdir():
                        if ArchiveTools.is_archive_file(file) or ImageTools.is_image_file(file):
                            paths.extend(str(file))
                else:
                    paths.append(path)

            self.__last_activated_file = self.filechooser.get_filenames()[0]
            self.files_chosen(paths)

            config['FILECHOOSER_LAST_BROWSED_PATH'] = self.filechooser.get_current_folder()
        else:
            self.files_chosen([])

        self.__destroyed = True

    def _update_preview(self, *args):
        path = self.filechooser.get_preview_filename()
        if path and Path.is_file(Path(path)):
            thumbnailer = Thumbnailer(size=(128, 128))
            thumbnailer.thumbnail_finished += self._preview_thumbnail_finished
            thumbnailer.thumbnail(path)
        else:
            self.__preview_image.clear()
            self.__namelabel.set_text('')
            self.__sizelabel.set_text('')

    def _preview_thumbnail_finished(self, filepath, pixbuf):
        """
        Called when the thumbnailer has finished creating the thumbnail for <filepath>
        """

        if self.__destroyed:
            return

        current_path = Path(self.filechooser.get_preview_filename())
        if current_path and current_path == filepath:
            if pixbuf is None:
                self.__preview_image.clear()
                self.__namelabel.set_text('')
                self.__sizelabel.set_text('')
            else:
                pixbuf = ImageTools.add_border(pixbuf, 1)
                self.__preview_image.set_from_pixbuf(pixbuf)
                self.__namelabel.set_text(Path(filepath).name)
                self.__sizelabel.set_text(FileSize(filepath).size)

    @staticmethod
    def _current_file():
        return None
        # XXX: This method defers the import of main to avoid cyclic imports during startup.
        # from mcomix import main
        # return main.main_window().filehandler.get_path_to_base()
