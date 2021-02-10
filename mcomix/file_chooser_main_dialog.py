# -*- coding: utf-8 -*-

"""file_chooser_main_dialog.py - Custom FileChooserDialog implementations"""

from mcomix.file_chooser_base_dialog import BaseFileChooserDialog
from mcomix.preferences import config
from pathlib import Path


class _MainFileChooserDialog(BaseFileChooserDialog):
    """The normal filechooser dialog used with the "Open" menu item"""

    def __init__(self, window):
        super().__init__(window)

        self.__window = window
        self.filechooser.set_select_multiple(True)
        self.add_archive_filters()
        self.add_image_filters()
        filters = self.filechooser.list_filters()
        self.filechooser.set_filter(filters[config['FILECHOOSER_LAST_FILTER']])

    def files_chosen(self, paths: list):
        if paths:
            filter_index = self.filechooser.list_filters().index(self.filechooser.get_filter())
            config['FILECHOOSER_LAST_FILTER'] = filter_index

            files = [Path(path) for path in paths]
            self.__window.filehandler.initialize_fileprovider(files)
            self.__window.filehandler.open_file(Path(files[0]))

        self.destroy()
