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
            if ArchiveTools.is_archive_file(Path(f)):
                # We found a sub-archive, don't try to extract it now, as we
                # must finish listing the containing archive contents before
                # any extraction can be done.
                sub_archive_list.append(f)
                continue

            if root is None:
                name = f
            else:
                name = Path() / root / f
            self.__entry_mapping[str(name)] = (archive, f)

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

    def iter_extract(self, wanted: set, destination_dir: Path):
        """
        List archive contents
        """

        # Unfortunately we can't just rely on BaseArchive default
        # implementation if solid archives are to be correctly supported:
        # we need to call iter_extract (not extract) for each archive ourselves.
        for archive in self.__archive_list:
            archive_wanted = {}
            for name in wanted:
                name_archive, name_archive_name = self.__entry_mapping[name]
                if name_archive == archive:
                    archive_wanted[name_archive_name] = name

            if not archive_wanted:
                continue

            root = self.__archive_root[archive]
            if root is None:
                archive_destination_dir = Path() / destination_dir
            else:
                archive_destination_dir = Path() / root

            logger.debug(f'Extracting from {archive.archive} to '
                         f'{archive_destination_dir}: {" ".join(archive_wanted.keys())}')

            for f in archive.iter_extract(set(archive_wanted.keys()), archive_destination_dir):
                yield archive_wanted[f]

            wanted -= set(archive_wanted.values())
            if not wanted:
                break

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
