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

import threading
import traceback
from pathlib import Path

from loguru import logger

from mcomix.archive.format_libarchive import LibarchiveExtractor
from mcomix.lib.events import Events, EventType
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

    def __init__(self, archive: Path):
        super().__init__()

        self.__events = Events()
        self.__threadpool = GlobalThreadPool().threadpool
        self.__condition = threading.Condition()

        self.__extractor = LibarchiveExtractor(archive)

    def list_contents(self):
        self.__threadpool.apply_async(
            self._list_contents,
            callback=self._list_contents_cb,
            error_callback=self._error_cb
        )

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
            self.__threadpool.apply_async(
                self._extract_all_files,
                error_callback=self._error_cb)

    def _file_listed(self, extractor, files: list):
        """
        Called after the contents of the archive has been listed
        """

        self.__events.run_events(EventType.FILE_LISTED, {'files': files})

    def _file_extracted(self, extractor, filename: Path):
        """
        Called whenever a new file is extracted and ready
        """

        self.__events.run_events(EventType.FILE_EXTRACTED, {'filename': filename})

    def close(self):
        """
        Close any open file objects, need only be called manually if the
        extract() method isn't called
        """

        self.stop()
        if self.__extractor:
            self.__extractor.close()

    def _extraction_finished(self, name: Path):
        if self.__threadpool.closed:
            return True

        with self.__condition:
            self.__condition.notify_all()

        self._file_extracted(self, name)

    def _extract_all_files(self):
        for name in self.__extractor.iter_extract():
            if self._extraction_finished(name):
                return

    def _list_contents(self):
        return [Path(self.__extractor.destination_path, image)
                for image in self.__extractor.iter_contents()]

    def _list_contents_cb(self, files: list):
        self._file_listed(self, files)

    def _error_cb(self, name, etype, value, tb):
        # Better to ignore any failed extractions (e.g. from a corrupt
        # archive) than to crash here and leave the main thread in a
        # possible infinite block. Damaged or missing files *should* be
        # handled gracefully by the main program anyway.

        logger.error(f'Extraction error: {value}')
        logger.error(f'Traceback:\n{"".join(traceback.format_tb(tb)).strip()}')
