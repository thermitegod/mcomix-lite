# -*- coding: utf-8 -*-

""" 7z archive extractor. """

import os
import shutil
import tempfile

from mcomix import process
from mcomix.archive import archive_base


class SevenZipArchive(archive_base.ExternalExecutableArchive):
    """ 7z file extractor using the 7z executable. """
    STATE_HEADER, STATE_LISTING, STATE_FOOTER = 1, 2, 3

    def __init__(self, archive):
        super(SevenZipArchive, self).__init__(archive)
        self._is_solid = False
        self._contents = []

    def _get_executable(self):
        return SevenZipArchive._find_7z_executable()

    def _get_list_arguments(self):
        args = [self._get_executable(), 'l', '-slt']
        args.extend(('--', self.archive))
        return args

    def _get_extract_arguments(self, list_file=None):
        args = [self._get_executable(), 'x', '-so']
        if list_file is not None:
            args.append('-i@' + list_file)
        args.extend(('--', self.archive))
        return args

    def _parse_list_output_line(self, line):
        """ Start parsing after the first delimiter (bunch of - characters),
        and end when delimiters appear again. Format:
        Date <space> Time <space> Attr <space> Size <space> Compressed <space> Name"""

        if line.startswith('----------'):
            if self._state == self.STATE_HEADER:
                # First delimiter reached, start reading from next line.
                self._state = self.STATE_LISTING
            elif self._state == self.STATE_LISTING:
                # Last delimiter read, stop reading from now on.
                self._state = self.STATE_FOOTER

            return None

        if self._state == self.STATE_HEADER:
            if 'Solid = +' == line:
                self._is_solid = True

        if self._state == self.STATE_LISTING:
            if line.startswith('Path = '):
                self._path = line[7:]
                return self._path
            if line.startswith('Size = '):
                filesize = int(line[7:])
                if filesize > 0:
                    self._contents.append((self._path, filesize))

        return None

    def is_solid(self):
        return self._is_solid

    def iter_contents(self):
        if not self._get_executable():
            return

        for retry_count in range(2):
            #: Indicates which part of the file listing has been read.
            self._state = self.STATE_HEADER
            #: Current path while listing contents.
            self._path = None
            with process.popen(self._get_list_arguments(), stderr=process.STDOUT, universal_newlines=True) as proc:
                for line in proc.stdout:
                    filename = self._parse_list_output_line(line.rstrip(os.linesep))
                    if filename is not None:
                        yield filename

        self.filenames_initialized = True

    def extract(self, filename, destination_dir):
        """ Extract <filename> from the archive to <destination_dir>. """
        assert isinstance(filename, str) and isinstance(destination_dir, str)

        if not self._get_executable():
            return

        if not self.filenames_initialized:
            self.list_contents()

        with tempfile.NamedTemporaryFile(mode='wt', prefix='mcomix.7z.') as tmplistfile:
            tmplistfile.write(filename + os.linesep)
            tmplistfile.flush()
            with self._create_file(os.path.join(destination_dir, filename)) as output:
                process.call(self._get_extract_arguments(list_file=tmplistfile.name),
                             stdout=output)

    def iter_extract(self, entries, destination_dir):
        if not self._get_executable():
            return

        if not self.filenames_initialized:
            self.list_contents()

        with process.popen(self._get_extract_arguments()) as proc:
            wanted = dict([(unicode_name, unicode_name) for unicode_name in entries])

            for filename, filesize in self._contents:
                data = proc.stdout.read(filesize)
                if filename not in wanted:
                    continue
                unicode_name = wanted.get(filename, None)
                if unicode_name is None:
                    continue
                with self._create_file(os.path.join(destination_dir, unicode_name)) as new:
                    new.write(data)
                yield unicode_name
                del wanted[filename]
                if 0 == len(wanted):
                    break

    @staticmethod
    def _find_7z_executable():
        """ Tries to start 7z, and returns either '7z' if
        it was started successfully or None otherwise. """
        exe = shutil.which('7z')
        if exe:
            return exe
        return None

    @staticmethod
    def is_available():
        return bool(SevenZipArchive._find_7z_executable())


class TarArchive(SevenZipArchive):
    """Special class for handling tar archives.

       Needed because for XZ archives, the technical listing
       does not contain the archive member name...
    """

    def __init__(self, archive):
        super(TarArchive, self).__init__(archive)
        self._is_solid = True

    def _get_extract_arguments(self, list_file=None):
        # Note: we ignore the list_file argument, which
        # contains our made up archive member name.
        return super(TarArchive, self)._get_extract_arguments()

    def iter_contents(self):
        if not self._get_executable():
            return
        self._state = self.STATE_HEADER
        # We make up a name that's guaranteed to be
        # recognized as an archive by MComix.
        self._path = 'archive.tar'
        with process.popen(self._get_list_arguments(), stderr=process.STDOUT) as proc:
            for line in proc.stdout:
                self._parse_list_output_line(line.rstrip(os.linesep))
        if self._contents:
            # The archive should not contain more than 1 member.
            assert 1 == len(self._contents)
            yield self._path
        self.filenames_initialized = True
