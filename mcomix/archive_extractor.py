# -*- coding: utf-8 -*-

"""archive_extractor.py - Archive extraction class"""

import os
import shutil
import threading
import traceback

from loguru import logger

from mcomix import archive_tools, callback, mt
from mcomix.preferences import prefs


class Extractor:
    """Extractor is a threaded class for extracting different archive formats.
    The Extractor can be loaded with paths to archives and a path to a
    destination directory. Once an archive has been set and its contents
    listed, it is possible to filter out the files to be extracted and set the
    order in which they should be extracted.  The extraction can then be
    started in a new thread in which files are extracted one by one, and a
    signal is sent on a condition after each extraction, so that it is possible
    for other threads to wait on specific files to be ready"""

    def __init__(self):
        self.__setupped = False
        self.__threadpool = mt.ThreadPool(
                name=self.__class__.__name__,
                processes=prefs['max extract threads'] or None)

        self.__src = None
        self.__files = None
        self.__extracted = None
        self.__archive = None

        self.__dst = None
        self.__contents_listed = False
        self.__extract_started = False
        self.__condition = None

    def setup(self, src, type=None):
        """Setup the extractor with archive <src> and destination dir <dst>.
        Return a threading.Condition related to the is_ready() method, or
        None if the format of <src> isn't supported"""
        self.__src = src
        self.__files = []
        self.__extracted = set()
        self.__archive = archive_tools.get_recursive_archive_handler(src, type=type, prefix='mcomix.')
        if self.__archive is None:
            logger.warning(msg := f'Non-supported archive format: \'{os.path.basename(src)}\'')
            raise ArchiveException(msg)

        self.__dst = self.__archive.get_destdir()
        self.__extract_started = False
        self.__condition = threading.Condition()
        self.__threadpool.apply_async(
                self._list_contents, callback=self._list_contents_cb,
                error_callback=self._list_contents_errcb)
        self.__setupped = True

        return self.__condition

    def get_files(self):
        """Return a list of names of all the files the extractor is currently
        set for extracting. After a call to setup() this is by default all
        files found in the archive. The paths in the list are relative to
        the archive root and are not absolute for the files once extracted"""
        with self.__condition:
            if not self.__contents_listed:
                return
            return self.__files[:]

    def get_directory(self):
        """Returns the root extraction directory of this extractor"""
        return self.__dst

    def set_files(self, files):
        """Set the files that the extractor should extract from the archive in
        the order of extraction. Normally one would get the list of all files
        in the archive using get_files(), then filter and/or permute this
        list before sending it back using set_files().

        Note: Random access on gzip or bzip2 compressed tar archives is
        no good idea. These formats are supported *only* for backwards
        compability. They are fine formats for some purposes, but should
        not be used for scanned comic books. So, we cheat and ignore the
        ordering applied with this method on such archives"""
        with self.__condition:
            if not self.__contents_listed:
                return
            self.__files[:] = [f for f in files if f not in self.__extracted]
            if not self.__files:
                # Nothing to do!
                return
            if self.__extract_started:
                self.extract()

    def is_ready(self, name):
        """Return True if the file <name> in the extractor's file list
        (as set by set_files()) is fully extracted"""
        with self.__condition:
            return name in self.__extracted

    def stop(self):
        """Signal the extractor to stop extracting and kill the extracting
        thread. Blocks until the extracting thread has terminated"""
        self.__threadpool.terminate()
        self.__threadpool.join()
        self.__threadpool.renew()
        if self.__setupped:
            self.__extract_started = False
            self.__setupped = False

    def extract(self):
        """Start extracting the files in the file list one by one using a
        new thread. Every time a new file is extracted a notify() will be
        signalled on the Condition that was returned by setup()"""
        with self.__condition:
            if not self.__contents_listed:
                return
            if not self.__extract_started:
                mt = self.__archive.support_concurrent_extractions \
                     and not self.__archive.is_solid()
                if mt:
                    self.__threadpool.ucbmap(
                            self._extract_file, self.__files,
                            callback=self._extraction_finished,
                            error_callback=self._extract_files_errcb)
                else:
                    self.__threadpool.apply_async(
                            self._extract_all_files,
                            error_callback=self._extract_files_errcb)

    @callback.Callback
    def contents_listed(self, extractor, files):
        """Called after the contents of the archive has been listed"""
        pass

    @callback.Callback
    def file_extracted(self, extractor, filename):
        """Called whenever a new file is extracted and ready"""
        pass

    def close(self):
        """Close any open file objects, need only be called manually if the
        extract() method isn't called"""
        self.stop()
        if self.__archive:
            logger.debug(f'Cache directory removed: \'{self.__dst}\'')
            self.__archive.close()

    def _extraction_finished(self, name):
        if self.__threadpool.closed:
            return
        with self.__condition:
            self.__files.remove(name)
            self.__extracted.add(name)
            self.__condition.notifyAll()
        self.file_extracted(self, name)

    def _extract_all_files(self):
        # With multiple extractions for each pass, some of the files might have
        # already been extracted.
        with self.__condition:
            files = list(set(self.__files) - self.__extracted)

        logger.debug(f'Extracting from \'{self.__src}\' to \'{self.__dst}\': \'{", ".join(files)}\'')
        for name in self.__archive.iter_extract(files, self.__dst):
            self._extraction_finished(name)

    def _extract_file(self, name):
        """Extract the file named <name> to the destination directory,
        mark the file as "ready", then signal a notify() on the Condition
        returned by setup()"""
        logger.debug(f'Extracting from \'{self.__src}\' to \'{self.__dst}\': \'{name}\'')
        self.__archive.extract(name)
        return name

    @staticmethod
    def _extract_files_errcb(name, etype, value, tb):
        # Better to ignore any failed extractions (e.g. from a corrupt
        # archive) than to crash here and leave the main thread in a
        # possible infinite block. Damaged or missing files *should* be
        # handled gracefully by the main program anyway.
        logger.error(f'Extraction error: {value}')
        logger.debug(f'Traceback:\n{"".join(traceback.format_tb(tb)).strip()}')

    def _list_contents(self):
        return [filename for filename in self.__archive.iter_contents()]

    def _list_contents_cb(self, files):
        with self.__condition:
            self.__files[:] = files
            self.__contents_listed = True
        self.contents_listed(self, files)

    @staticmethod
    def _list_contents_errcb(name, etype, value, tb):
        logger.error(f'Extraction error: {value}')
        logger.debug(f'Traceback:\n{"".join(traceback.format_tb(tb)).strip()}')


class ArchiveException(Exception):
    """Indicate error during extraction operations"""
    pass
