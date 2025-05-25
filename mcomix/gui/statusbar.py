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

from pathlib import Path

from gi.repository import Gtk

from mcomix.file_size import format_filesize
from mcomix.preferences import config
from mcomix.view_state import ViewState


class Statusbar(Gtk.Box):
    def __init__(self):
        super().__init__()

        # statusbar field separator
        self.__sep = '  |  '

        # Status text layout
        # page number, file number, page resolution, archive filename,
        # page filename, page filesize, archive filesize, view mode
        self.__status = Gtk.Statusbar()
        self.__context_id = self.__status.get_context_id('statusbar')

        # margin padding, gtk3 defaults are too large
        self.__status.set_margin_top(2)
        self.__status.set_margin_bottom(2)

        self.add(self.__status)

        # Default status information
        self.__total_page_numbers = ''
        self.__total_file_numbers = ''
        self.__page_resolution = ''
        self.__archive_filename = ''
        self.__page_filename = ''
        self.__page_filesize = ''
        self.__archive_filesize = ''
        self.__current_view_mode = ''

        self.show_all()

    def set_message(self, message: str):
        """
        Set a specific message (such as an error message) on the statusbar,
        replacing whatever was there earlier
        """

        self.__status.pop(self.__context_id)
        self.__status.push(self.__context_id, f'    {message}')

    def set_page_number(self, page: int, total_pages: int):
        """
        Update the page number
        """

        if ViewState.is_displaying_double:
            if ViewState.is_manga_mode:
                p = f'{page + 1}, {page}'
            else:
                p = f'{page}, {page + 1}'
        else:
            p = f'{page}'

        self.__total_page_numbers = f'{p} / {total_pages}'

    def set_view_mode(self):
        """
        Update the mode
        """

        if ViewState.is_manga_mode:
            self.__current_view_mode = 'Manga'
        else:
            self.__current_view_mode = 'Western'

    def set_file_number(self, fileno: int, total: int):
        """
        Updates the file number (i.e. number of current file/total files loaded)
        """

        self.__total_file_numbers = f'{fileno} / {total}'

    def set_resolution(self, scaled_sizes: list[list[int]], size_list: list[list[int]]):
        """
        Update the resolution data.
        Takes an iterable of tuples, (x, y, scale), describing the original
        resolution of an image as well as the currently displayed scale
        """

        resolutions = [(*size, scaled_size[0] / size[0]) for scaled_size, size in zip(scaled_sizes, size_list, strict=True)]
        if ViewState.is_manga_mode:
            resolutions.reverse()

        if config['STATUSBAR_SHOW_SCALE']:
            self.__page_resolution = ', '.join(f'{d[0]}x{d[1]} ({d[2]:.2%})' for d in resolutions)
        else:
            self.__page_resolution = ', '.join(f'{d[0]}x{d[1]}' for d in resolutions)

    def set_archive_filename(self, root: Path):
        """
        Set the name of the root (directory or archive)
        """

        self.__archive_filename = str(root)

    def set_filename(self, filename: str):
        """
        Update the filename
        """

        self.__page_filename = filename

    def set_filesize(self, size: str):
        """
        Update the filesize
        """

        if size is None:
            size = ''
        self.__page_filesize = size

    def set_filesize_archive(self, path: Path):
        """
        Update the filesize
        """

        self.__archive_filesize = format_filesize(path)

    def update(self):
        """
        Set the statusbar to display the current state
        """

        text = ''

        if config['STATUSBAR_FIELD_PAGE_NUMBERS']:
            text += f'{self.__total_page_numbers}{self.__sep}'
        if config['STATUSBAR_FIELD_FILE_NUMBERS']:
            text += f'{self.__total_file_numbers}{self.__sep}'
        if config['STATUSBAR_FIELD_PAGE_RESOLUTION']:
            text += f'{self.__page_resolution}{self.__sep}'
        if config['STATUSBAR_FIELD_ARCHIVE_NAME']:
            text += f'{self.__archive_filename}{self.__sep}'
        if config['STATUSBAR_FIELD_PAGE_FILENAME']:
            text += f'{self.__page_filename}{self.__sep}'
        if config['STATUSBAR_FIELD_PAGE_FILESIZE']:
            text += f'{self.__page_filesize}{self.__sep}'
        if config['STATUSBAR_FIELD_ARCHIVE_FILESIZE']:
            text += f'{self.__archive_filesize}{self.__sep}'
        if config['STATUSBAR_FIELD_VIEW_MODE']:
            text += f'{self.__current_view_mode}{self.__sep}'

        self.set_message(message=text.strip(self.__sep))
