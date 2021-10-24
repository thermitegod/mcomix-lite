# -*- coding: utf-8 -*-

from enum import Enum
from pathlib import Path

from PIL import Image


# disable PIL DecompressionBombWarning
Image.MAX_IMAGE_PIXELS = None

# formats supported by PIL
Image.init()


class ImageSupported(Enum):
    # formats supported by PIL
    EXTS = set([ext for ext in Image.EXTENSION
                if ext not in ('.pdf',)])

    @classmethod
    def is_image_file(cls, path: Path):
        return path.suffix.lower() in cls.EXTS.value
