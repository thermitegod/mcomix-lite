# -*- coding: utf-8 -*-

"""archive_extractor.py - Archive extraction class"""

import threading
from pathlib import Path

from loguru import logger

from mcomix.archive_tools import ArchiveTools
from mcomix.lib.callback import Callback
from mcomix.lib.exceptions import ArchiveException
from mcomix.lib.threadpool import GlobalThreadPool


class Extractor:
    """
    Extractor is a threaded class for extracting different archive formats.
    The Extractor can be loaded with paths to archives and a path to a
    destination directory. Once an archive has been set and its contents
    listed, it is possible to filter out the files to be extracted and set the
    order in which they should be extracted.  The extraction can then be
    started in a new thread in which files are extracted one by one, and a
    signal is sent on a condition after each extraction, so that it is possible
    for other threads to wait on specific files to be ready
    """

    def __init__(self):
        super().__init__()

        self.__threadpool = GlobalThreadPool.threadpool

        self.__src = None
        self.__files = None
        self.__extracted = None
        self.__archive = None

        self.__contents_listed = False
        self.__condition = None

    def setup(self, src: Path, archive_type: int = None):
        """
        Setup the extractor with archive <src> and destination dir <dst>.
        Return a threading.Condition related to the is_ready() method, or
        None if the format of <src> isn't supported
        """

        self.__src = src
        self.__files = []
        self.__extracted = set()
        self.__archive = ArchiveTools.get_archive_interface_handler(path=self.__src, archive_type=archive_type)
        if self.__archive is None:
            logger.warning(f'Non-supported archive format: \'{self.__src.name}\'')
            raise ArchiveException

        self.__condition = threading.Condition()
        self.__threadpool.apply_async(
            self._list_contents, callback=self._list_contents_cb,
            error_callback=self._error_cb)

        return self.__condition

    def get_directory(self):
        """
        Returns the root extraction directory of this extractor
        """

        return self.__archive.get_destdir()

    def set_files(self, files: list):
        """
        Set the files that the extractor should extract from the archive in
        the order of extraction. Normally one would get the list of all files
        in the archive using get_files(), then filter and/or permute this
        list before sending it back using set_files().

        Note: Random access on gzip or bzip2 compressed tar archives is
        no good idea. These formats are supported *only* for backwards
        compability. They are fine formats for some purposes, but should
        not be used for scanned comic books. So, we cheat and ignore the
        ordering applied with this method on such archives
        """

        with self.__condition:
            if not self.__contents_listed:
                return
            self.__files = [f for f in files.copy() if f not in self.__extracted]
            if not self.__files:
                # Nothing to do!
                return

    def stop(self):
        """
        Signal the extractor to stop extracting and kill the extracting
        thread. Blocks until the extracting thread has terminated
        """

        self.__threadpool.terminate()
        self.__threadpool.join()
        self.__threadpool.renew()

    def extract(self):
        """
        Start extracting the files in the file list one by one using a
        new thread. Every time a new file is extracted a notify() will be
        signalled on the Condition that was returned by setup()
        """

        with self.__condition:
            if not self.__contents_listed:
                return

            self.__threadpool.apply_async(
                self._extract_all_files,
                error_callback=self._error_cb)

    @Callback
    def contents_listed(self, extractor, files: list):
        """
        Called after the contents of the archive has been listed
        """

        pass

    @Callback
    def file_extracted(self, extractor, filename: str):
        """
        Called whenever a new file is extracted and ready
        """

        pass

    def close(self):
        """
        Close any open file objects, need only be called manually if the
        extract() method isn't called
        """

        self.stop()
        if self.__archive:
            self.__archive.close()

    def _extraction_finished(self, name: str):
        if self.__threadpool.closed:
            return True
        with self.__condition:
            self.__files.remove(name)
            self.__extracted.add(name)
            self.__condition.notify_all()
        self.file_extracted(self, name)

    def _extract_all_files(self):
        # With multiple extractions for each pass, some of the files might have
        # already been extracted.
        with self.__condition:
            files = list(set(self.__files) - self.__extracted)

        for name in self.__archive.iter_extract(files):
            if self._extraction_finished(name):
                return

    def _list_contents(self):
        return [filename for filename in self.__archive.iter_contents()]

    def _list_contents_cb(self, files: list):
        with self.__condition:
            self.__files = files.copy()
            self.__contents_listed = True
        self.contents_listed(self, files)

    @staticmethod
    def _error_cb(name, etype, value, tb):
        # Better to ignore any failed extractions (e.g. from a corrupt
        # archive) than to crash here and leave the main thread in a
        # possible infinite block. Damaged or missing files *should* be
        # handled gracefully by the main program anyway.

        logger.error(f'Extraction error: {value}')
