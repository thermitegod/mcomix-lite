# -*- coding: utf-8 -*-

class ArchiveException(Exception):
    """
    Indicate error during extraction operations
    """

    pass


class MissingPixbuf(Exception):
    """
    Indicate error about missing pixbuf
    """
    pass
