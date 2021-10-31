# -*- coding: utf-8 -*-

"""archive_extractor.py - Archive extraction class"""

import threading
import traceback
from pathlib import Path

from loguru import logger

from mcomix.archive.format_libarchive import LibarchiveExtractor
from mcomix.lib.callback import Callback
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

        self.__archive_destination_dir = None
        self.__extractor = None

        self.__contents = []
        self.__contents_listed = False
        self.__condition = threading.Condition()

    def setup(self, archive: Path):
        """
        Setup the extractor with archive <src> and destination dir <dst>.
        Return a threading.Condition related to the is_ready() method, or
        None if the format of <src> isn't supported
        """

        self.__contents_listed = False

        self.__extractor = LibarchiveExtractor(archive)
        self.__archive_destination_dir = Path() / self.__extractor.destdir / 'main_archive'

        self.__threadpool.apply_async(
            self._list_contents, callback=self._list_contents_cb,
            error_callback=self._error_cb)

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
    def contents_listed(self, extractor, files: set):
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
        if self.__extractor:
            self.__extractor.close()

    def _extraction_finished(self, name: str):
        if self.__threadpool.closed:
            return True

        with self.__condition:
            self.__condition.notify_all()

        self.file_extracted(self, name)

    def _extract_all_files(self):
        for name in self.__extractor.iter_extract(self.__archive_destination_dir):
            if self._extraction_finished(str(name)):
                return

    def _list_contents(self):
        if self.__contents_listed:
            return set(self.__contents)

        self.__contents = []
        for f in self.__extractor.iter_contents():
            filename = str(Path(self.__archive_destination_dir, f))
            self.__contents.append(filename)

        self.__contents_listed = True

        return set(self.__contents)

    def _list_contents_cb(self, files: set):
        with self.__condition:
            self.__contents_listed = True

        self.contents_listed(self, files)

    def _error_cb(self, name, etype, value, tb):
        # Better to ignore any failed extractions (e.g. from a corrupt
        # archive) than to crash here and leave the main thread in a
        # possible infinite block. Damaged or missing files *should* be
        # handled gracefully by the main program anyway.

        logger.error(f'Extraction error: {value}')
        logger.error(f'Traceback:\n{"".join(traceback.format_tb(tb)).strip()}')
