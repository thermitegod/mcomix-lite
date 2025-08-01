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

from __future__ import annotations

import mimetypes
from pathlib import Path

from gi.repository import GdkPixbuf

from loguru import logger

import mcomix.image_tools as image_tools

from mcomix.file_size import format_filesize
from mcomix.image_files import ImageFiles
from mcomix.lib.events import Events, EventType
from mcomix.lib.threadpool import GlobalThreadPool, Lock
from mcomix.preferences import config
from mcomix.view_state import ViewState


class ImageHandler():
    """
    The ImageHandler keeps track of images, pages, caches and reads files.
    When the Filehandler's methods refer to pages, they are indexed from 1,
    i.e. the first page is page 1 etc.
    Other modules should *never* read directly from the files pointed to by
    paths given by the ImageHandler's methods. The files are not even
    guaranteed to exist at all times since the extraction of archives is
    threaded
    """

    def __init__(self):
        super().__init__()

        self.__events = Events()
        self.__events.add_event(EventType.FILE_AVAILABLE, self.file_available)

        self.__image_files = ImageFiles()

        #: Caching thread
        self.__threadpool = GlobalThreadPool().threadpool
        self.__lock = Lock()
        self.__cache_lock = {}
        #: Current page
        self.__current_image: int = None
        #: Set of images reading for decoding (i.e. already extracted)
        self.__available_images = set()
        #: List of pixbufs we want to cache
        self.__wanted_pixbufs: list[int] = []
        #: Pixbuf map from page > Pixbuf
        self.__raw_pixbufs: dict[int, GdkPixbuf] = {}

    @property
    def image_files(self):
        return self.__image_files

    def cleanup(self):
        # __del__ does not work for this, and there are no cpp like destructors
        self.__events.remove_event(EventType.FILE_AVAILABLE, self.file_available)

    def _get_pixbuf(self, page: int) -> GdkPixbuf:
        """
        Return the pixbuf indexed by <page> from cache.
        Pixbufs not found in cache are fetched from disk first
        """

        self._cache_pixbuf(page, force_return=False)
        return self.__raw_pixbufs[page]

    def get_pixbufs(self, number_of_bufs: int) -> list[GdkPixbuf]:
        """
        Returns number_of_bufs pixbufs for the image(s) that should be
        currently displayed. This method might fetch images from disk, so make
        sure that number_of_bufs is as small as possible
        """

        return [self._get_pixbuf(self.__current_image + i) for i in range(number_of_bufs)]

    def do_caching(self) -> None:
        """
        Make sure that the correct pixbufs are stored in cache. These
        are (in the current implementation) the current image(s), and
        if cacheing is enabled, also the one or two pixbufs before and
        after the current page. All other pixbufs are deleted and garbage
        collected directly in order to save memory
        """

        if not self.__lock.acquire():
            return

        # Get list of wanted pixbufs.
        self.__wanted_pixbufs = self._ask_for_pages(self.get_current_page())

        # remove old pixbufs.
        for page in set(self.__raw_pixbufs) - set(self.__wanted_pixbufs):
            del self.__raw_pixbufs[page]

        logger.debug(f'Caching page(s): {self.__wanted_pixbufs}')

        # Start caching available images not already in cache.
        wanted_pixbufs = [page for page in self.__wanted_pixbufs
                          if page in self.__available_images]
        self.__threadpool.map_async(self._cache_pixbuf, wanted_pixbufs)

        self.__lock.release()

    def _cache_pixbuf(self, page: int, force_return: bool = True) -> None:
        with self.__cache_lock[page]:
            if page in self.__raw_pixbufs:
                return
            with self.__lock:
                if page not in self.__wanted_pixbufs and force_return:
                    return
            logger.debug(f'Caching page: {page}')
            try:
                pixbuf = image_tools.load_pixbuf(self.__image_files.get_path_from_page(page))
            except Exception as ex:
                logger.error(f'Could not load pixbuf for page: {page}')
                logger.debug(f'Exception: {ex}')
                pixbuf = None
            self.__raw_pixbufs[page] = pixbuf

    def set_page(self, page: int) -> None:
        """
        Set up filehandler to the page <page_num>
        """

        self.__current_image = page
        self.do_caching()

    def is_page_available(self, page: int = None) -> bool:
        """
        Returns True if <page> is available and calls to get_pixbufs
        would not block. If <page> is None, the current page(s) are assumed
        """

        if page is None:
            page = self.get_current_page()

        page_list = [page]
        if ViewState.is_displaying_double and not self.is_last_page(page):
            page_list.append(page + 1)

        for page in page_list:
            if page not in self.__available_images:
                return False

        return True

    def page_available(self, page: int) -> None:
        """
        Called whenever a new page becomes available, i.e. the corresponding file has been extracted
        """

        logger.debug(f'Page is available: {page}')

        self.__cache_lock[page] = Lock()
        self.__available_images.add(page)

        # Check if we need to cache it.
        if page in self.__wanted_pixbufs:
            self.__threadpool.apply_async(self._cache_pixbuf, (page,))

        self.__events.run_events(EventType.PAGE_AVAILABLE, {'page': page})

    def file_available(self, filename: Path) -> None:
        """
        Called by the filehandler when a new file becomes available
        """

        # Find the page that corresponds to <filename>
        self.page_available(self.__image_files.get_page_from_path(filename))

    def get_number_of_pages(self) -> int:
        """
        Return the number of pages in the current archive/directory
        """

        return self.__image_files.get_total_pages()

    def get_current_page(self) -> int:
        """
        Return the current page number (starting from 1), or 0 if no file is loaded
        """

        if self.__current_image is None:
            return 0

        return self.__current_image

    def is_last_page(self, page: int = None) -> bool:
        """
        is <page> the last in a book, if page is None use current page
        """

        if page is None:
            page = self.get_current_page()

        return page == self.__image_files.get_total_pages()

    def get_path_to_page(self, page: int = None) -> Path:
        """
        Return the full path to the image file for <page>, or the current page if <page> is None
        """

        if page is None:
            page = self.__current_image

        return self.__image_files.get_path_from_page(page)

    def _get_page_unknown(self) -> str:
        if ViewState.is_displaying_double:
            return ['unknown', 'unknown']
        return ['unknown']

    def get_page_filename(self, page: int = None) -> str:
        """
        :param page
            A page number or if None the current page
        :returns
            [page, page + 1] if ViewState.displayed_double is True else return [page]
        """

        if not self.is_page_available(page=page):
            return self._get_page_unknown()

        if page is None:
            page = self.get_current_page()

        page_data = [self.get_path_to_page(page).name]

        if ViewState.is_displaying_double:
            page_data.append(self.get_path_to_page(page + 1).name)

            if ViewState.is_manga_mode:
                page_data.reverse()

        return page_data

    def get_page_filesize(self, page: int = None) -> list[str]:
        """
        :param page
            A page number or if None the current page
        :returns
            [page, page + 1] if ViewState.displayed_double is True else return [page]
        """

        if not self.is_page_available(page=page):
            return self._get_page_unknown()

        if page is None:
            page = self.get_current_page()

        page_data = [format_filesize(self.get_path_to_page(page))]

        if ViewState.is_displaying_double:
            page_data.append(format_filesize(self.get_path_to_page(page + 1)))

            if ViewState.is_manga_mode:
                page_data.reverse()

        return page_data

    def get_page_size(self, page: int = None) -> tuple[int, int]:
        """
        Return a tuple (width, height) with the size of <page>. If <page>
        is None, return the size of the current page
        """

        if page is None:
            page = self.get_current_page()

        if not self.is_page_available(page):
            return 0, 0
        pixbuf = self._get_pixbuf(page)
        return (pixbuf.get_width(), pixbuf.get_height())

    def get_mime_name(self, page: int = None) -> str:
        """
        Return a string with the name of the mime type of <page>. If
        <page> is None, return the mime type name of the current page
        """

        page_path = self.get_path_to_page(page)
        if not Path.is_file(page_path):
            return None

        mime_type, _ = mimetypes.guess_type(page_path)
        if mime_type:
            return mime_type
        return None

    def get_thumbnail(self, page: int, size: int) -> GdkPixbuf:
        """
        Return a thumbnail pixbuf of <page> that fit in a box with
        dimensions <width>x<height>. Return a thumbnail for the current
        page if <page> is None.
        If <nowait> is True, don't wait for <page> to be available
        """

        if not self._is_page_extracted(page=page):
            # Page is not available!
            return None

        path = self.get_path_to_page(page)
        return image_tools.create_thumbnail(path=path, size=size)

    def _is_page_extracted(self, page: int) -> bool:
        if page is None:
            page = self.get_current_page()

        if page in self.__available_images:
            # page is extracted
            return True

        # page is not extracted
        return False

    def _ask_for_pages(self, page: int) -> list[int]:
        """
        Ask for pages around <page> to be given priority extraction
        """

        total_pages = self.get_number_of_pages()

        cache_start = page - config['PAGE_CACHE_BEHIND']
        if cache_start < 1:
            cache_start = 1

        cache_end = page + config['PAGE_CACHE_FORWARD']
        if cache_end > total_pages:
            cache_end = total_pages

        return list(range(cache_start, cache_end))
