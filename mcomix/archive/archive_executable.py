# -*- coding: utf-8 -*-

"""
Base class for unified handling of various archive formats. Used for simplifying
extraction and adding new archive formats
"""

from pathlib import Path

from mcomix.archive.archive_base import BaseArchive
from mcomix.lib.process import Process


class BaseArchiveExecutable(BaseArchive):
    """
    Base archive interface. All filenames passed from and into archives
    are expected to be Unicode objects. Archive files are converted to
    Unicode with some guess-work
    """

    STATE_HEADER = 1
    STATE_LISTING = 2
    STATE_FOOTER = 3

    def __init__(self, archive):
        super().__init__(archive)

        self.archive = archive

        self.state = None
        self.path = None
        self.contents = []

    def extract(self, filename: str, destination_dir: Path):
        """
        Extracts the file specified by <filename> and return the path of it.
        This filename must be obtained by calling list_contents().
        The file is saved to <destination_dir>

        :param filename: file to extract
        :type filename: str
        :param destination_dir: extraction path
        :type destination_dir: Path
        :returns: full path of the extracted file
        :rtype: Path
        """

        destination_path = Path() / destination_dir / filename

        with self.lock:
            with self._create_file(destination_path) as output:
                Process.call(self._get_extract_arguments(), stdout=output)

    def iter_contents(self):
        #: Indicates which part of the file listing has been read.
        self.state = self.STATE_HEADER
        #: Current path while listing contents.
        self.path = None

        with self.lock:
            with Process.popen(self._get_list_arguments(),
                               stderr=Process.STDOUT,
                               universal_newlines=True) as proc:
                for line in proc.stdout:
                    filename = self._parse_list_output_line(line.rstrip('\n'))
                    if filename is not None:
                        yield filename

    def iter_extract(self, entries, destination_dir: Path):
        with self.lock:
            with Process.popen(self._get_extract_arguments()) as proc:
                wanted = dict([(unicode_name, unicode_name) for unicode_name in entries])

                for filename, filesize in self.contents:
                    data = proc.stdout.read(filesize)
                    if filename not in wanted:
                        continue
                    unicode_name = wanted.get(filename, None)
                    if unicode_name is None:
                        continue

                    destination_path = Path() / destination_dir / unicode_name
                    with self._create_file(destination_path) as new:
                        new.write(data)
                    yield unicode_name
                    del wanted[filename]
                    if not wanted:
                        break
