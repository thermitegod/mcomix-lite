# -*- coding: utf-8 -*-

"""Class for transparently handling an archive containing sub-archives"""

import os
import tempfile

from mcomix import archive_tools, log
from mcomix.archive import archive_base
from mcomix.preferences import prefs


class RecursiveArchive(archive_base.BaseArchive):
    def __init__(self, archive, prefix='mcomix.'):
        super(RecursiveArchive, self).__init__(archive.archive)
        self._main_archive = archive
        self._tempdir = tempfile.TemporaryDirectory(prefix=prefix, dir=prefs['temporary directory'])
        self._sub_tempdirs = []
        self.destdir = self._tempdir.name
        self._archive_list = []
        # Map entry name to its archive+name.
        self._entry_mapping = {}
        # Map archive to its root.
        self._archive_root = {}
        self._contents_listed = False
        self._contents = []
        # Assume concurrent extractions are not supported.
        self.support_concurrent_extractions = False

    def _iter_contents(self, archive, root=None):
        if not root:
            root = os.path.join(self.destdir, 'main_archive')
        self._archive_list.append(archive)
        self._archive_root[archive] = root
        sub_archive_list = []
        for f in archive.iter_contents():
            if archive_tools.is_archive_file(f):
                # We found a sub-archive, don't try to extract it now, as we
                # must finish listing the containing archive contents before
                # any extraction can be done.
                sub_archive_list.append(f)
                continue
            name = f
            if root is not None:
                name = os.path.join(root, name)
            self._entry_mapping[name] = (archive, f)
            yield name
        for f in sub_archive_list:
            # Extract sub-archive.
            destination_dir = self.destdir
            if root is not None:
                destination_dir = os.path.join(destination_dir, root)
            sub_archive_path = archive.extract(f, destination_dir)
            # And open it and list its contents.
            sub_archive = archive_tools.get_archive_handler(sub_archive_path)
            if sub_archive is None:
                log.warning('Non-supported archive format: %s', os.path.basename(sub_archive_path))
                continue
            sub_tempdir = tempfile.TemporaryDirectory(
                prefix='sub_archive.{:04}.'.format(len(self._archive_list)), dir=self.destdir)
            sub_root = sub_tempdir.name
            self._sub_tempdirs.append(sub_tempdir)
            for name in self._iter_contents(sub_archive, sub_root):
                yield name

    def _check_concurrent_extraction_support(self):
        supported = True
        # We need all archives to support concurrent extractions.
        for archive in self._archive_list:
            if not archive.support_concurrent_extractions:
                supported = False
                break
        self.support_concurrent_extractions = supported

    def iter_contents(self):
        if self._contents_listed:
            for f in self._contents:
                yield f
            return
        self._contents = []
        for f in self._iter_contents(self._main_archive):
            self._contents.append(f)
            yield f
        self._contents_listed = True
        # We can now check if concurrent extractions are really supported.
        self._check_concurrent_extraction_support()

    def list_contents(self):
        if self._contents_listed:
            return self._contents
        return [f for f in self.iter_contents()]

    def extract(self, filename):
        if not self._contents_listed:
            self.list_contents()
        archive, name = self._entry_mapping[filename]
        root = self._archive_root[archive]
        destination_dir = self.destdir
        if root is not None:
            destination_dir = os.path.join(destination_dir, root)
        log.debug('extracting from %s to %s: %s', archive.archive, destination_dir, filename)
        return archive.extract(name, destination_dir)

    def iter_extract(self, entries, destination_dir):
        if not self._contents_listed:
            self.list_contents()
        # Unfortunately we can't just rely on BaseArchive default
        # implementation if solid archives are to be correctly supported:
        # we need to call iter_extract (not extract) for each archive ourselves.
        wanted = set(entries)
        for archive in self._archive_list:
            archive_wanted = {}
            for name in wanted:
                name_archive, name_archive_name = self._entry_mapping[name]
                if name_archive == archive:
                    archive_wanted[name_archive_name] = name
            if 0 == len(archive_wanted):
                continue
            root = self._archive_root[archive]
            archive_destination_dir = destination_dir
            if root is not None:
                archive_destination_dir = os.path.join(destination_dir, root)
            log.debug('extracting from %s to %s: %s',
                      archive.archive, archive_destination_dir, ' '.join(archive_wanted.keys()))
            for f in archive.iter_extract(archive_wanted.keys(), archive_destination_dir):
                yield archive_wanted[f]
            wanted -= set(archive_wanted.values())
            if 0 == len(wanted):
                break

    def is_solid(self):
        if not self._contents_listed:
            self.list_contents()
        # We're solid if at least one archive is solid.
        for archive in self._archive_list:
            if archive.is_solid():
                return True
        return False

    def close(self):
        # close all archives before cleanup temporary directory
        for archive in self._archive_list:
            archive.close()
        for tempdir in self._sub_tempdirs:
            tempdir.cleanup()
        self._tempdir.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
