# -*- coding: utf-8 -*-

"""image_handler.py - Image handler that takes care of cacheing and giving out images"""

import bisect
from pathlib import Path

from loguru import logger

from mcomix.constants import Constants
from mcomix.image_tools import ImageTools
from mcomix.lib.callback import Callback
from mcomix.lib.mt import GlobalThreadPool, Lock
from mcomix.preferences import config
from mcomix.thumbnail_tools import Thumbnailer
from mcomix.utils import Utils


class ImageHandler:
    """
    The FileHandler keeps track of images, pages, caches and reads files.
    When the Filehandler's methods refer to pages, they are indexed from 1,
    i.e. the first page is page 1 etc.
    Other modules should *never* read directly from the files pointed to by
    paths given by the FileHandler's methods. The files are not even
    guaranteed to exist at all times since the extraction of archives is
    threaded
    """

    def __init__(self, window):
        super().__init__()

        #: Reference to main window
        self.__window = window

        #: Caching thread
        self.__threadpool = GlobalThreadPool.threadpool
        self.__lock = Lock()
        self.__cache_lock = {}
        #: Archive path, if currently opened file is archive
        self.__base_path = None
        #: List of image file names, either from extraction or directory
        self.__image_files = []
        #: Index of current page
        self.__current_image_index = None
        #: Set of images reading for decoding (i.e. already extracted)
        self.__available_images = set()
        #: List of pixbufs we want to cache
        self.__wanted_pixbufs = []
        #: Pixbuf map from page > Pixbuf
        self.__raw_pixbufs = {}
        #: How many pages to keep in cache
        self.__cache_pages = config['MAX_PAGES_TO_CACHE']

        self.__window.filehandler.file_available += self._file_available

    def _get_pixbuf(self, index: int):
        """
        Return the pixbuf indexed by <index> from cache.
        Pixbufs not found in cache are fetched from disk first
        """

        self._cache_pixbuf(index)
        return self.__raw_pixbufs[index]

    def get_pixbufs(self, number_of_bufs: int):
        """
        Returns number_of_bufs pixbufs for the image(s) that should be
        currently displayed. This method might fetch images from disk, so make
        sure that number_of_bufs is as small as possible
        """

        result = []
        for i in range(number_of_bufs):
            result.append(self._get_pixbuf(self.__current_image_index + i))
        return result

    def do_cacheing(self):
        """
        Make sure that the correct pixbufs are stored in cache. These
        are (in the current implementation) the current image(s), and
        if cacheing is enabled, also the one or two pixbufs before and
        after the current page. All other pixbufs are deleted and garbage
        collected directly in order to save memory
        """

        if not self.__lock.acquire(blocking=False):
            return
        try:
            if not self.__window.filehandler.get_file_loaded():
                return

            # Get list of wanted pixbufs.
            wanted_pixbufs = self._ask_for_pages(self.get_current_page())

            # remove old pixbufs.
            for index in set(self.__raw_pixbufs) - set(wanted_pixbufs):
                del self.__raw_pixbufs[index]

            logger.debug(f'Caching page(s): \'{" ".join([str(index + 1) for index in wanted_pixbufs])}\'')

            self.__wanted_pixbufs = wanted_pixbufs.copy()
            # Start caching available images not already in cache.
            wanted_pixbufs = [index for index in wanted_pixbufs
                              if index in self.__available_images]
            self.__threadpool.map_async(self._cache_pixbuf, wanted_pixbufs)
        finally:
            self.__lock.release()

    def _cache_pixbuf(self, index: int):
        self._wait_on_page(index + 1)
        with self.__cache_lock[index]:
            if index in self.__raw_pixbufs:
                return
            with self.__lock:
                if index not in self.__wanted_pixbufs:
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
        self.do_cacheing()

    def set_image_files(self, files: list):
        # Set list of image file names
        self.__image_files = files.copy()

    def set_base_path(self, path: Path):
        self.__base_path = path

    def get_current_path(self):
        # Get current image path
        try:
            return self.__image_files[self.__current_image_index]
        except IndexError:
            logger.warning(f'failed to get current image path')
            return ''

    def get_virtual_double_page(self, page: int = None):
        """
        Return True if the current state warrants use of virtual
        double page mode (i.e. if double page mode is on, the corresponding
        preference is set, and one of the two images that should normally
        be displayed has a width that exceeds its height), or if currently
        on the first page

        :returns: True if the current state warrants use of virtual double page mode
        :rtype: bool
        """

        if page is None:
            page = self.get_current_page()

        if (page == 1 and
                config['VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES'] & Constants.DOUBLE_PAGE['AS_ONE_TITLE'] and
                self.__window.filehandler.get_archive_type() is not None):
            return True

        if (not config['DEFAULT_DOUBLE_PAGE'] or
                not config['VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES'] & Constants.DOUBLE_PAGE['AS_ONE_WIDE'] or
                page == self.get_number_of_pages()):
            return False

        for page in (page, page + 1):
            if not self.page_is_available(page):
                return False
            pixbuf = self._get_pixbuf(page - 1)
            width, height = pixbuf.get_width(), pixbuf.get_height()
            if config['AUTO_ROTATE_FROM_EXIF']:
                rotation = ImageTools.get_implied_rotation(pixbuf)

                # if rotation not in (0, 90, 180, 270):
                #     return

                if rotation in (90, 270):
                    width, height = height, width
            if width > height:
                return True

        return False

    def get_real_path(self):
        """
        Return the "real" path to the currently viewed file, i.e. the
        full path to the archive or the full path to the currently viewed image
        """

        if self.__window.filehandler.get_archive_type() is not None:
            return self.__window.filehandler.get_path_to_base()
        return self.get_path_to_page()

    def cleanup(self):
        """
        Run clean-up tasks. Should be called prior to exit
        """

        self.__threadpool.renew()
        self.__wanted_pixbufs.clear()
        while self.__cache_lock:
            index, lock = self.__cache_lock.popitem()
            with lock:
                self.__base_path = None
                self.__image_files.clear()
                self.__current_image_index = None
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
            if self.__window.displayed_double() and current_page < len(self.__image_files):
                index_list.append(current_page)
        else:
            index_list = [page - 1]

        for index in index_list:
            if index not in self.__available_images:
                return False

        return True

    @Callback
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

    @staticmethod
    def bin_search(lst: list, value: str):
        """
        Binary search for sorted list C{lst}, looking for C{value}.

        :returns: List index on success. On failure, it returns the 1's
        complement of the index where C{value} would be inserted.
        This implies that the return value is non-negative if and only if
        C{value} is contained in C{lst}
        """

        index = bisect.bisect_left(lst, value)
        if index != len(lst) and lst[index] == value:
            return index

        return ~index

    def _file_available(self, filepaths: list):
        """
        Called by the filehandler when a new file becomes available
        """

        # Find the page that corresponds to <filepath>
        if not self.__image_files:
            return

        available = sorted(filepaths)
        for i, imgpath in enumerate(self.__image_files):
            if self.bin_search(available, imgpath) >= 0:
                self.page_available(i + 1)

    def get_number_of_pages(self):
        """
        Return the number of pages in the current archive/directory
        """

        return len(self.__image_files)

    def get_current_page(self):
        """
        Return the current page number (starting from 1), or 0 if no file is loaded
        """

        if self.__current_image_index is not None:
            return self.__current_image_index + 1

        return 0

    def get_path_to_page(self, page: int = None):
        """
        Return the full path to the image file for <page>, or the current page if <page> is None
        """

        if page is None:
            index = self.__current_image_index
        else:
            index = page - 1

        if isinstance(index, int) and 0 <= index < len(self.__image_files):
            return Path(self.__image_files[index])

        return Path('')

    def get_page_filename(self, page: int = None, double: bool = False, manga: bool = False):
        """
        Return the filename of the <page>, or the filename of the
        currently viewed page if <page> is None. If <double> is True, return
        a tuple (p, p') where p is the filename of <page> (or the current
        page) and p' is the filename of the page after
        """

        if not self.page_is_available():
            if double:
                return '', ''
            return ''

        def get_fname(fname):
            path = self.get_path_to_page(fname)
            if not Path.is_file(path):
                return ''
            return path.name

        if page is None:
            page = self.get_current_page()

        first = get_fname(page)

        if double:
            second = get_fname(page + 1)
            if manga:
                return second, first
            return first, second

        return first

    def get_page_filesize(self, page: int = None, double: bool = False, manga: bool = False):
        """
        Return the filesize of the <page>, or the filesize of the
        currently viewed page if <page> is None. If <double> is True, return
        a tuple (s, s') where s is the filesize of <page> (or the current
        page) and s' is the filesize of the page after
        """

        if not self.page_is_available():
            if double:
                return '-1', '-1'
            return '-1'

        def get_fsize(fsize):
            path = self.get_path_to_page(fsize)
            try:
                if Path.exists(path):
                    fsize = Path.stat(path).st_size
                else:
                    fsize = 0
            except OSError:
                logger.warning(f'failed to get file size for: {path}')
                fsize = 0
            return Utils.format_byte_size(fsize)

        if page is None:
            page = self.get_current_page()

        first = get_fsize(page)

        if double:
            second = get_fsize(page + 1)
            if manga:
                return second, first
            return first, second

        return first

    def get_current_filename(self):
        """
        Return a string with the name of the currently viewed file that is suitable for printing
        """

        if self.__window.filehandler.get_archive_type() is not None:
            return Path(self.__base_path).name

        return self.get_current_path()

    def get_size(self, page: int = None):
        """
        Return a tuple (width, height) with the size of <page>. If <page>
        is None, return the size of the current page
        """

        self._wait_on_page(page)

        page_path = self.get_path_to_page(page)
        if not Path.is_file(page_path):
            return 0, 0

        return ImageTools.get_image_size(page_path)

    def get_mime_name(self, page: int = None):
        """
        Return a string with the name of the mime type of <page>. If
        <page> is None, return the mime type name of the current page
        """

        self._wait_on_page(page)

        page_path = self.get_path_to_page(page)
        if not Path.is_file(page_path):
            return None

        return ImageTools.get_image_mime(page_path)

    def get_thumbnail(self, page: int = None, size: tuple = (128, 128), nowait: bool = False):
        """
        Return a thumbnail pixbuf of <page> that fit in a box with
        dimensions <width>x<height>. Return a thumbnail for the current
        page if <page> is None.
        If <nowait> is True, don't wait for <page> to be available
        """

        if not self._wait_on_page(page, check_only=nowait):
            # Page is not available!
            return None

        path = self.get_path_to_page(page)
        if not Path.is_file(path):
            return None

        try:
            thumbnailer = Thumbnailer(size=size)
            return thumbnailer.thumbnail(path)
        except Exception as ex:
            logger.error(f'Failed to create thumbnail for image: \'{path}\'')
            logger.error(f'Exception: {ex}')
            return None

    def _wait_on_page(self, page: int, check_only: bool = False):
        """
        Block the running (main) thread until the file corresponding to
        image <page> has been fully extracted.
        If <check_only> is True, only check (and return status), don't wait
        """

        if page is None:
            index = self.__current_image_index
        else:
            index = page - 1
        if index in self.__available_images:
            # Already extracted!
            return True
        if check_only:
            # Asked for check only...
            return False

        logger.debug(f'Waiting for page: \'{page}\'')
        path = self.get_path_to_page(page)
        self.__window.filehandler.wait_on_file(path)
        return True

    def _ask_for_pages(self, page: int):
        """
        Ask for pages around <page> to be given priority extraction
        """

        total_pages = self.get_number_of_pages()

        page -= 1
        harf = self.__cache_pages // 2 - 1
        start = max(0, page - harf)
        end = start + self.__cache_pages
        page_list = list(range(total_pages)[start:end])

        if end > total_pages:
            start = page_list[0] - (self.__cache_pages - len(page_list))
            page_list.extend(range(max(0, start), page_list[0]))
        page_list.sort()

        # move page before now to the end
        pos = page_list.index(page)
        head = page_list[:pos]
        page_list = page_list[pos:].copy()
        page_list.extend(reversed(head))

        logger.debug(f'Ask for priority extraction around page: \'{page + 1}\': '
                     f'\'{" ".join([str(n + 1) for n in page_list])}\'')

        files = [self.__image_files[index]
                 for index in page_list
                 if index not in self.__available_images]

        if files:
            self.__window.filehandler.ask_for_files(files)

        return page_list
