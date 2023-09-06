# -*- coding: utf-8 -*-

from __future__ import annotations

import shutil
from pathlib import Path

from gi.repository import Gtk
from loguru import logger
from send2trash import send2trash

from mcomix.file_handler import FileHandler
from mcomix.image_handler import ImageHandler
from mcomix.message_dialog.info import MessageDialogInfo
from mcomix.message_dialog.remember import MessageDialogRemember
from mcomix.lib.events import Events, EventType
from mcomix.preferences import config
from mcomix.state.view_state import ViewState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class FileSystemActions:
    def __init__(self, window: MainWindow):
        super().__init__()

        self.__window = window

        self.__events = Events()
        self.__events.add_event(EventType.KB_EXTRACT_PAGE, self.extract_page)
        self.__events.add_event(EventType.KB_FILE_MOVE, self.move_file)
        self.__events.add_event(EventType.KB_FILE_TRASH, self.trash_file)

        self.__file_handler = FileHandler(None)
        self.__image_handler = ImageHandler()

    def extract_page(self):
        """
        Derive some sensible filename (the filename should do) and offer
        the user the choice to save the current page with the selected name
        """

        page = self.__image_handler.get_current_page()

        if ViewState.is_displaying_double:
            # asks for left or right page if in double page mode
            # and not showing a single page

            response_left = 70
            response_right = 80

            dialog = MessageDialogRemember()
            dialog.add_buttons('Left', response_left)
            dialog.add_buttons('Right', response_right)
            dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
            dialog.set_default_response(Gtk.ResponseType.CANCEL)
            dialog.set_text(primary='Extract Left or Right page?')
            result = dialog.run()

            if result not in (response_left, response_right):
                return None

            if result == response_left:
                if ViewState.is_manga_mode:
                    page += 1
            elif result == response_right:
                if not ViewState.is_manga_mode:
                    page += 1

        page_name = self.__image_handler.get_page_filename(page=page)[0]
        page_path = self.__image_handler.get_path_to_page(page=page)

        save_dialog = Gtk.FileChooserDialog(title='Save page as', action=Gtk.FileChooserAction.SAVE)
        save_dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        save_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        save_dialog.set_modal(True)
        save_dialog.set_transient_for(self.__window)
        save_dialog.set_do_overwrite_confirmation(True)
        save_dialog.set_current_name(page_name)

        if save_dialog.run() == Gtk.ResponseType.ACCEPT and save_dialog.get_filename():
            shutil.copy(page_path, save_dialog.get_filename())

        save_dialog.destroy()

    def move_file(self):
        """
        The currently opened file/archive will be moved to prefs['MOVE_FILE']
        """

        current_file = self.__file_handler.get_real_path()

        target_dir = Path() / current_file.parent / config['MOVE_FILE']
        target_file = Path() / target_dir / current_file.name

        if not Path.exists(target_dir):
            target_dir.mkdir()

        try:
            self._load_next_file()
        except Exception:
            logger.error('File action failed: move_file()')

        if current_file.is_file():
            Path.rename(current_file, target_file)

        if not target_file.is_file():
            dialog = MessageDialogInfo()
            dialog.set_text(primary='File was not moved', secondary=f'{target_file}')
            dialog.run()

    def trash_file(self):
        """
        The currently opened file/archive will be trashed after showing a confirmation dialog
        """

        current_file = self.__file_handler.get_real_path()

        dialog = MessageDialogRemember()
        dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.add_buttons(Gtk.STOCK_DELETE, Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_should_remember_choice('delete-opend-file', (Gtk.ResponseType.OK,))
        dialog.set_text('Trash Selected File?', secondary=f'{current_file.name}')
        result = dialog.run()
        if result != Gtk.ResponseType.OK:
            return

        try:
            self._load_next_file()
        except Exception:
            logger.error('File action failed: trash_file()')

        if current_file.is_file():
            send2trash(bytes(current_file))

        if current_file.is_file():
            dialog = MessageDialogInfo()
            dialog.set_text(primary='File was not deleted', secondary=f'{current_file}')
            dialog.run()

    def _load_next_file(self):
        """
        Shared logic for move_file() and trash_file()
        """

        if self.__file_handler.is_archive():
            next_opened = self.__file_handler.open_archive_direction(forward=True)
            if not next_opened:
                next_opened = self.__file_handler.open_archive_direction(forward=False)
            if not next_opened:
                self.__file_handler.close_file()
        else:
            if self.__image_handler.get_number_of_pages() > 1:
                # Open the next/previous file
                if self.__image_handler.is_last_page():
                    self.__events.run_events(EventType.KB_PAGE_FLIP, {'number_of_pages': -1})
                else:
                    self.__events.run_events(EventType.KB_PAGE_FLIP, {'number_of_pages': 1})

                # Refresh the directory
                self.__file_handler.refresh_file()
            else:
                self.__file_handler.close_file()
