# -*- coding: utf-8 -*-

"""Class for transparently handling an archive containing sub-archives"""

from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger

from mcomix.archive_tools import ArchiveTools


class ArchiveRecursive:
    def __init__(self, archive):
        super().__init__()

        self.__main_archive = archive

        self.__destdir = archive.destdir

        self.__sub_tempdirs = []
        self.__archive_list = []
        # Map entry name to its archive+name.
        self.__entry_mapping = {}
        # Map archive to its root.
        self.__archive_root = {}
        self.__contents_listed = False
        self.__contents = []

    def get_destdir(self):
        """
        Get the directry that the archive will be extracted to

        :return: path to extraction dir
        """

        return self.__destdir

    def _iter_contents(self, archive, root: Path = None):
        if root is None:
            root = Path() / self.__destdir / 'main_archive'

        self.__archive_list.append(archive)
        self.__archive_root[archive] = root

        sub_archive_list = []
        for f in archive.iter_contents():
            # cast from <class 'libarchive.entry.ArchiveEntry'>
            filename = Path(str(f))
            # print(f'archive file: {f}, {type(f)}')


            if ArchiveTools.is_archive_file(filename):
                # We found a sub-archive, don't try to extract it now, as we
                # must finish listing the containing archive contents before
                # any extraction can be done.
                sub_archive_list.append(str(filename))
                continue

            if root is None:
                name = filename
            else:
                name = Path() / root / filename
            self.__entry_mapping[str(name)] = (archive, str(filename))

            yield str(name)

        for f in sub_archive_list:
            # Extract sub-archive.
            if root is None:
                destination_dir = self.__destdir
            else:
                destination_dir = Path() / self.__destdir / root

            sub_archive_path = archive.extract(filename=f, destination_dir=destination_dir)
            # And open it and list its contents.
            sub_archive_type = ArchiveTools.archive_mime_type(path=sub_archive_path)
            sub_archive = ArchiveTools.get_archive_handler(path=sub_archive_path, archive_type=sub_archive_type)

            if sub_archive is None:
                logger.warning(f'Non-supported archive format: {Path(sub_archive_path).name}')
                continue

            sub_tempdir = TemporaryDirectory(
                prefix=f'sub_archive.{len(self.__archive_list):04}.',
                dir=self.__destdir)
            sub_root = Path(sub_tempdir.name)
            self.__sub_tempdirs.append(sub_tempdir)

            for name in self._iter_contents(archive=sub_archive, root=sub_root):
                yield name

    def iter_contents(self):
        """
        Generator for listing the archive contents
        """

        if self.__contents_listed:
            for f in self.__contents:
                yield f
            return

        self.__contents = []
        for f in self._iter_contents(archive=self.__main_archive):
            self.__contents.append(f)
            yield f

        self.__contents_listed = True

    def iter_extract(self, destination_dir: Path):
        """
        extract archive and return an iter of archive contents
        """
        print(self.__archive_list)

        for archive in self.__archive_list:
            root = self.__archive_root[archive]
            if root is None:
                archive_destination_dir = Path() / destination_dir
            else:
                archive_destination_dir = Path() / root

            for f in archive.iter_extract(archive_destination_dir):
                yield str(f)

    def close(self):
        """
        Close the archive handle before cleanup temporary directory
        """

        for archive in self.__archive_list:
            archive.close()
        for tempdir in self.__sub_tempdirs:
            tempdir.cleanup()

        archive.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
