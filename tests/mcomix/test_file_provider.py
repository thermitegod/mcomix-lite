from pathlib import Path

from mcomix.file_provider import GetFileProvider, OrderedFileProvider, PreDefinedFileProvider


def test_file_provider_ordered():
    filelist = [Path('test_01.zip')]
    get_provider = GetFileProvider()
    provider = get_provider.get_file_provider(filelist)

    assert isinstance(provider, OrderedFileProvider)


def test_file_provider_predefined():
    filelist = [Path('test_01.zip'), Path('test_02.zip')]
    get_provider = GetFileProvider()
    provider = get_provider.get_file_provider(filelist)

    assert isinstance(provider, PreDefinedFileProvider)
