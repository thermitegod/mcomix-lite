# -*- coding: utf-8 -*-

""" RAR archive extractor. """

import os
import shutil

from mcomix import process
from mcomix.archive import archive_base


class RarArchive(archive_base.ExternalExecutableArchive):
    """ RAR file extractor using the unrar/rar executable. """
    STATE_HEADER, STATE_LISTING = 1, 2

    def __init__(self, archive):
        super(RarArchive, self).__init__(archive)
        self._is_solid = False
        self._contents = []

    def _get_executable(self):
        return self._find_unrar_executable()

    def _get_list_arguments(self):
        args = [self._get_executable(), 'vt']
        args.extend(('--', self.archive))
        return args

    def _get_extract_arguments(self):
        args = [self._get_executable(), 'p', '-inul', '-@']
        args.extend(('--', self.archive))
        return args

    def _parse_list_output_line(self, line):
        if self._state == self.STATE_HEADER:
            if line.startswith('Details: '):
                flags = line[9:].split(', ')
                if 'solid' in flags:
                    self._is_solid = True
                self._state = self.STATE_LISTING
                return None
        if self._state == self.STATE_LISTING:
            line = line.lstrip()
            if line.startswith('Name: '):
                self._path = line[6:]
                return self._path
            if line.startswith('Size: '):
                filesize = int(line[6:])
                if filesize > 0:
                    self._contents.append((self._path, filesize))
            if line.startswith('Flags: '):
                flags = line[7:].split()
                if 'solid' in flags:
                    self._is_solid = True

        return None

    def is_solid(self):
        return self._is_solid

    def iter_contents(self):
        if not self._get_executable():
            return

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

        cmd = self._get_extract_arguments() + [filename]
        with self._create_file(os.path.join(destination_dir, filename)) as output:
            process.call(cmd, stdout=output)

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
    def _find_unrar_executable():
        """ start unrar, Return None if could not be started. """
        exe = shutil.which('unrar')
        if exe:
            return exe
        return None

    @staticmethod
    def is_available():
        return bool(RarArchive._find_unrar_executable())
