# -*- coding: utf-8 -*-

"""image_handler.py - Image handler that takes care of cacheing and giving out images"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from mcomix.file_size import FileSize
from mcomix.image_tools import ImageTools
from mcomix.lib.events import Events, EventType
from mcomix.lib.metaclass import SingleInstanceMetaClass
from mcomix.lib.threadpool import GlobalThreadPool, Lock
from mcomix.preferences import config
from mcomix.state.view_state import ViewState
from mcomix.thumbnailer import Thumbnailer


class ImageHandler(metaclass=SingleInstanceMetaClass):
    """
    The FileHandler keeps track of images, pages, caches and reads files.
    When the Filehandler's methods refer to pages, they are indexed from 1,
    i.e. the first page is page 1 etc.
    Other modules should *never* read directly from the files pointed to by
    paths given by the FileHandler's methods. The files are not even
    guaranteed to exist at all times since the extraction of archives is
    threaded
    """

    def __init__(self):
        super().__init__()

        self.__events = Events()
        self.__events.add_event(EventType.FILE_AVAILABLE, self.file_available)

        #: Caching thread
        self.__threadpool = GlobalThreadPool.threadpool
        self.__lock = Lock()
        self.__cache_lock = {}
        #: List of image file names, either from extraction or directory
        self.__image_files = []
        #: Dict of image file names with and index
        self.__image_files_index = {}
        #: Total number of pages
        self.__image_files_total = 0
        #: Index of current page
        self.__current_image_index = None
        #: Set of images reading for decoding (i.e. already extracted)
        self.__available_images = set()
        #: List of pixbufs we want to cache
        self.__wanted_pixbufs = []
        #: Pixbuf map from page > Pixbuf
        self.__raw_pixbufs = {}

        self.__thumbnailer = Thumbnailer()

    def get_pixbuf(self, index: int):
        """
        Return the pixbuf indexed by <index> from cache.
        Pixbufs not found in cache are fetched from disk first
        """

        self._cache_pixbuf(index, force_return=False)
        return self.__raw_pixbufs[index]

    def get_pixbufs(self, number_of_bufs: int):
        """
        Returns number_of_bufs pixbufs for the image(s) that should be
        currently displayed. This method might fetch images from disk, so make
        sure that number_of_bufs is as small as possible
        """

        return [self.get_pixbuf(self.__current_image_index + i) for i in range(number_of_bufs)]

    def do_caching(self):
        """
        Make sure that the correct pixbufs are stored in cache. These
        are (in the current implementation) the current image(s), and
        if cacheing is enabled, also the one or two pixbufs before and
        after the current page. All other pixbufs are deleted and garbage
        collected directly in order to save memory
        """

        if not self.__lock.acquire(blocking=False):
            return

        # Get list of wanted pixbufs.
        self.__wanted_pixbufs = self._ask_for_pages(self.get_current_page())

        # remove old pixbufs.
        for index in set(self.__raw_pixbufs) - set(self.__wanted_pixbufs):
            del self.__raw_pixbufs[index]

        logger.debug(f'Caching page(s): {self.__wanted_pixbufs}')

        # Start caching available images not already in cache.
        wanted_pixbufs = [index for index in self.__wanted_pixbufs
                          if index in self.__available_images]
        self.__threadpool.map_async(self._cache_pixbuf, wanted_pixbufs)

        self.__lock.release()

    def _cache_pixbuf(self, index: int, force_return: bool = True):
        with self.__cache_lock[index]:
            if index in self.__raw_pixbufs:
                return
            with self.__lock:
                if index not in self.__wanted_pixbufs and force_return:
                    return
            logger.debug(f'Caching page: \'{index + 1}\'')
            try:
                pixbuf = ImageTools.load_pixbuf(self.__image_files[index])
            except Exception as ex:
                logger.error(f'Could not load pixbuf for page: \'{index + 1}\'')
                logger.error(f'Exception: {ex}')
                pixbuf = None
            self.__raw_pixbufs[index] = pixbuf

    def set_page(self, page_num: int):
        """
        Set up filehandler to the page <page_num>
        """

        # if 0 > page_num > self.get_number_of_pages():
        #     return

        self.__current_image_index = page_num - 1
        self.do_caching()

    def set_image_files(self, files: list):
        # Set list of image file names
        self.__image_files = files
        self.__image_files_total = len(self.__image_files)
        self.__image_files_index = dict(zip(self.__image_files, range(self.__image_files_total), strict=True))

    def cleanup(self):
        """
        Run clean-up tasks. Should be called prior to exit
        """

        self.__threadpool.renew()
        self.__wanted_pixbufs.clear()
        while self.__cache_lock:
            self.__cache_lock.popitem()

        self.__image_files.clear()
        self.__image_files_total = 0
        self.__current_image_index = None
        self.__image_files_index.clear()
        self.__available_images.clear()
        self.__raw_pixbufs.clear()

    def page_is_available(self, page: int = None):
        """
        Returns True if <page> is available and calls to get_pixbufs
        would not block. If <page> is None, the current page(s) are assumed
        """

        if page is None:
            current_page = self.get_current_page()
            if not current_page:
                # Current 'book' has no page.
                return False
            index_list = [current_page - 1]
            if ViewState.is_displaying_double and not self.is_last_page(current_page):
                index_list.append(current_page)
        else:
            index_list = [page - 1]

        for index in index_list:
            if index not in self.__available_images:
                return False

        return True

    def page_available(self, page: int):
        """
        Called whenever a new page becomes available, i.e. the corresponding file has been extracted
        """

        logger.debug(f'Page is available: \'{page}\'')
        index = page - 1

        # if index in self.__available_images:
        #     return

        self.__cache_lock[index] = Lock()
        self.__available_images.add(index)

        # Check if we need to cache it.
        if index in self.__wanted_pixbufs:
            self.__threadpool.apply_async(self._cache_pixbuf, (index,))

        self.__events.run_events(EventType.PAGE_AVAILABLE, page)

    def file_available(self, filepath: Path):
        """
        Called by the filehandler when a new file becomes available
        """

        # Find the page that corresponds to <filepath>
        self.page_available(self.__image_files_index[filepath] + 1)

    def get_number_of_pages(self):
        """
        Return the number of pages in the current archive/directory
        """

        return self.__image_files_total

    def get_current_page(self):
        """
        Return the current page number (starting from 1), or 0 if no file is loaded
        """

        if self.__current_image_index is None:
            return 0

        return self.__current_image_index + 1

    def is_last_page(self, page: int = None):
        """
        is <page> the last in a book, if page is None use current page
        """

        if page is None:
            page = self.get_current_page()

        return page == self.__image_files_total

    def get_path_to_page(self, page: int = None):
        """
        Return the full path to the image file for <page>, or the current page if <page> is None
        """

        if page is None:
            index = self.__current_image_index
        else:
            index = page - 1

        try:
            return Path(self.__image_files[index])
        except IndexError:
            return None

    def _get_page_unknown(self):
        if ViewState.is_displaying_double:
            return ['unknown', 'unknown']
        return ['unknown']

    def get_page_filename(self, page: int = None):
        """
        :param page
            A page number or if None the current page
        :returns
            [page, page + 1] if ViewState.displayed_double is True else return [page]
        """

        if not self.page_is_available(page=page):
            return self._get_page_unknown()

        if page is None:
            page = self.get_current_page()

        page_data = [self.get_path_to_page(page).name]

        if ViewState.is_displaying_double:
            page_data.append(self.get_path_to_page(page + 1).name)

            if ViewState.is_manga_mode:
                page_data.reverse()

        return page_data

    def get_page_filesize(self, page: int = None):
        """
        :param page
            A page number or if None the current page
        :returns
            [page, page + 1] if ViewState.displayed_double is True else return [page]
        """

        if not self.page_is_available(page=page):
            return self._get_page_unknown()

        if page is None:
            page = self.get_current_page()

        page_data = [FileSize(self.get_path_to_page(page))]

        if ViewState.is_displaying_double:
            page_data.append(FileSize(self.get_path_to_page(page + 1)))

            if ViewState.is_manga_mode:
                page_data.reverse()

        return page_data

    def get_size(self, page: int = None):
        """
        Return a tuple (width, height) with the size of <page>. If <page>
        is None, return the size of the current page
        """

        page_path = self.get_path_to_page(page)
        if not Path.is_file(page_path):
            return 0, 0

        return ImageTools.get_image_size(page_path)

    def get_mime_name(self, page: int = None):
        """
        Return a string with the name of the mime type of <page>. If
        <page> is None, return the mime type name of the current page
        """

        page_path = self.get_path_to_page(page)
        if not Path.is_file(page_path):
            return None

        return ImageTools.get_image_mime(page_path)

    def get_thumbnail(self, page: int, size: tuple):
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
        if not Path.is_file(path):
            return None

        return self.__thumbnailer(size=size, filepath=path)

    def _is_page_extracted(self, page: int):
        if page is None:
            index = self.__current_image_index
        else:
            index = page - 1
        if index in self.__available_images:
            # page is extracted
            return True

        # page is not extracted
        return False

    def _ask_for_pages(self, page: int):
        """
        Ask for pages around <page> to be given priority extraction
        """

        total_pages = self.get_number_of_pages()

        page -= 1

        cache_start = page - config['PAGE_CACHE_BEHIND']
        if cache_start < 0:
            cache_start = 0

        cache_end = page + config['PAGE_CACHE_FORWARD']
        if cache_end > total_pages:
            cache_end = total_pages

        return list(range(cache_start, cache_end))
