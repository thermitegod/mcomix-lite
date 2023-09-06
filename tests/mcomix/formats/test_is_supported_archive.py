import pytest
from pathlib import Path

from mcomix.formats.archive import ArchiveSupported


@pytest.mark.parametrize('archive', [
    Path('test.zip'),
    Path('test.cbz'),

    Path('test.rar'),
    Path('test.cbr'),

    Path('test.7z'),
    Path('test.cb7'),

    Path('test.tar'),
    Path('test.cbt'),

    Path('test.tar.gz'),
    Path('test.tar.bz2'),
    Path('test.tar.lzma'),
    Path('test.tar.xz'),
    Path('test.tar.lz4'),
    Path('test.tar.zst'),

    Path('test.lrzip'),
    Path('test.lzip'),

    Path('test.lha'),
    Path('test.lzh'),
])
def test_is_archive(archive: Path):
    assert ArchiveSupported.is_archive_file(archive)


@pytest.mark.parametrize('not_archive', [
    (Path('test.not')),
    (Path('test.an')),
    (Path('test.archive')),
    (Path('test.file')),

])
def test_is_not_archive(not_archive: Path):
    assert not ArchiveSupported.is_archive_file(not_archive)
