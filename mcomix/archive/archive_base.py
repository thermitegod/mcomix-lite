# -*- coding: utf-8 -*-

""" Base class for unified handling of various archive formats. Used for simplifying
extraction and adding new archive formats. """

import errno
import os
import threading

from mcomix import process


class BaseArchive(object):
    """ Base archive interface. All filenames passed from and into archives
    are expected to be Unicode objects. Archive files are converted to
    Unicode with some guess-work. """

    """ True if concurrent calls to extract is supported. """
    support_concurrent_extractions = False

    def __init__(self, archive):
        assert isinstance(archive, str), 'File should be an Unicode string.'

        self.archive = archive
        self._event = threading.Event()

    def iter_contents(self):
        """Generator for listing the archive contents"""
        return
        yield

    def list_contents(self):
        """ Returns a list of unicode filenames relative to the archive root.
        These names do not necessarily exist in the actual archive since they
        need to saveable on the local filesystems, so some characters might
        need to be replaced. """

        return [f for f in self.iter_contents()]

    def extract(self, filename, destination_dir):
        """ Extracts the file specified by <filename>. This filename must
        be obtained by calling list_contents(). The file is saved to
        <destination_dir>. """

        assert isinstance(filename, str) and isinstance(destination_dir, str)

    def iter_extract(self, entries, destination_dir):
        """ Generator to extract <entries> from archive to <destination_dir>. """
        wanted = set(entries)
        for filename in self.iter_contents():
            if filename not in wanted:
                continue
            self.extract(filename, destination_dir)
            yield filename
            wanted.remove(filename)
            if 0 == len(wanted):
                break

    def close(self):
        """ Closes the archive and releases held resources. """
        pass

    def is_solid(self):
        """ Returns True if the archive is solid and extraction should be done
        in one pass. """
        return False

    @staticmethod
    def _create_directory(directory):
        """ Recursively create a directory if it doesn't exist yet. """
        if os.path.exists(directory):
            return
        try:
            os.makedirs(directory)
        except OSError as e:
            # Can happen with concurrent calls.
            if e.errno != errno.EEXIST:
                raise e

    def _create_file(self, dst_path):
        """ Open <dst_path> for writing, making sure base directory exists. """
        dst_dir = os.path.dirname(dst_path)
        # Create directory if it doesn't exist
        self._create_directory(dst_dir)
        return open(dst_path, 'wb')


class ExternalExecutableArchive(BaseArchive):
    """ For archives that are extracted by spawning an external
    application. """

    # Since we're using an external program for extraction,
    # concurrent calls are supported.
    support_concurrent_extractions = True

    def __init__(self, archive):
        super(ExternalExecutableArchive, self).__init__(archive)
        # Flag to determine if list_contents() has been called
        # This builds the Unicode mapping and is likely required
        # for extracting filenames that have been internally mapped.
        self.filenames_initialized = False

    def _get_executable(self):
        """ Returns the executable's name or path. Return None if no executable
        was found on the system. """
        raise NotImplementedError('Subclasses must override _get_executable.')

    def _get_list_arguments(self):
        """ Returns an array of arguments required for the executable
        to produce a list of archive members. """
        raise NotImplementedError('Subclasses must override _get_list_arguments.')

    def _get_extract_arguments(self):
        """ Returns an array of arguments required for the executable
        to extract a file to STDOUT. """
        raise NotImplementedError('Subclasses must override _get_extract_arguments.')

    def _parse_list_output_line(self, line):
        """ Parses the output of the external executable's list command
        and return either a file path relative to the archive's root,
        or None if the current line doesn't contain any file references. """

        return line

    def iter_contents(self):
        if not self._get_executable():
            return

        with process.popen([self._get_executable()] +
                           self._get_list_arguments() +
                           [self.archive]) as proc:
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

        with self._create_file(os.path.join(destination_dir, filename)) as output:
            process.call([self._get_executable()] +
                         self._get_extract_arguments() +
                         [self.archive, filename],
                         stdout=output)
