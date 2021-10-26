# -*- coding: utf-8 -*-

from enum import Enum
from pathlib import Path


class ArchiveSupported(Enum):
    EXTS = set(
        (
            '.zip', '.cbz',
            '.rar', '.cbr',
            '.7z', '.cb7',
            '.tar', '.cbt',
            '.gz', '.bz2', '.lzma', '.xz', '.lz4', '.zst',
            '.lrzip', '.lzip',
            '.lha', '.lzh',
        )
    )

    @classmethod
    def is_archive_file(cls, path: Path):
        return path.suffix.lower() in cls.EXTS.value

