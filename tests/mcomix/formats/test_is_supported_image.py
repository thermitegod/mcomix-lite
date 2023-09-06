import pytest
from pathlib import Path

from mcomix.formats.image import ImageSupported


@pytest.mark.parametrize('image', [
    Path('test.jpeg'),
    Path('test.jpg'),
    Path('test.png'),

    # Path('test.ppm'),
    # Path('test.ppn'),
])
def test_is_archive(image: Path):
    assert ImageSupported.is_image_file(image)


@pytest.mark.parametrize('not_image', [
    Path('test.pdf'),  # make sure .pdf files are not detected as supported

    Path('test.not'),
    Path('test.an'),
    Path('test.image'),
    Path('test.file'),
])
def test_is_not_archive(not_image: Path):
    assert not ImageSupported.is_image_file(not_image)
