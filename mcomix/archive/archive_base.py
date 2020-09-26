# -*- coding: utf-8 -*-

"""
Base class for unified handling of various archive formats. Used for simplifying
extraction and adding new archive formats
"""

from pathlib import Path

from mcomix.lib import process


class BaseArchive:
    """
    Base archive interface. All filenames passed from and into archives
    are expected to be Unicode objects. Archive files are converted to
    Unicode with some guess-work
    """

    # True if concurrent calls to extract is supported
    support_concurrent_extractions = False

    def __init__(self, archive):
        super().__init__()

        self.archive = archive

    def iter_contents(self):
        """
        Generator for listing the archive contents
        """

        yield

    def list_contents(self):
        """
        These names do not necessarily exist in the actual archive since they
        need to saveable on the local filesystems, so some characters might
        need to be replaced

        :returns a list of unicode filenames relative to the archive root.
        """

        return [filename for filename in self.iter_contents()]

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

        raise NotImplementedError('Subclasses must override extract.')

    def iter_extract(self, entries, destination_dir: Path):
        """
        Generator to extract <entries> from archive to <destination_dir>

        :type entries
        :param destination_dir: Path
        """

        wanted = set(entries)
        for filename in self.iter_contents():
            if filename not in wanted:
                continue
            self.extract(filename, destination_dir)
            yield filename
            wanted.remove(filename)
            if not wanted:
                break

    def close(self):
        """
        Closes the archive and releases held resources
        """

        pass

    def is_solid(self):
        """
        Check if the archive is solid since extraction will vary if it is True

        :returns: is True if the archive is solid and extraction should be done in one pass
        :rtype: bool
        """

        return False

    @staticmethod
    def _create_file(dst_path):
        """
        Open <dst_path> for writing, making sure base directory exists

        :returns: created image path
        :rtype: buffer
        """

        dst_dir = Path(dst_path).parent

        # Create directory if it doesn't exist
        if not Path.exists(dst_dir):
            dst_dir.mkdir(parents=True, exist_ok=True)

        return Path.open(dst_path, 'wb')


class ExternalExecutableArchive(BaseArchive):
    """
    For archives that are extracted by spawning an external application
    """

    # Since we're using an external program for extraction,
    # concurrent calls are supported.
    support_concurrent_extractions = True

    def __init__(self, archive):
        super().__init__(archive)

        # Flag to determine if list_contents() has been called
        # This builds the Unicode mapping and is likely required
        # for extracting filenames that have been internally mapped.
        self.__filenames_initialized = False

    def _get_executable(self):
        """
        Returns the executable's name or path. Return None if no executable
        was found on the system
        """

        raise NotImplementedError('Subclasses must override _get_executable.')

    def _get_list_arguments(self):
        """
        Returns an array of arguments required for the executable
        to produce a list of archive members
        """

        raise NotImplementedError('Subclasses must override _get_list_arguments.')

    def _get_extract_arguments(self):
        """
        Returns an array of arguments required for the executable
        to extract a file to STDOUT
        """

        raise NotImplementedError('Subclasses must override _get_extract_arguments.')

    def _parse_list_output_line(self, line):
        """
        Parses the output of the external executable's list command
        and return either a file path relative to the archive's root,
        or None if the current line doesn't contain any file references
        """

        raise NotImplementedError('Subclasses must override _parse_list_output_line.')

    def extract(self, filename: str, destination_dir: Path):
        """
        Extract <filename> from the archive to <destination_dir>

        :param filename: file to extract
        :type filename: str
        :param destination_dir: extraction path
        :type destination_dir: Path
        :returns: full path of the extracted file
        :rtype: Path
        """

        raise NotImplementedError('Subclasses must override extract.')
