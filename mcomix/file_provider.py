# -*- coding: utf-8 -*-

from mcomix.providers.file_provider_ordered import OrderedFileProvider
from mcomix.providers.file_provider_predefined import PreDefinedFileProvider


class GetFileProvider:
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_file_provider(filelist: list):
        """
        Initialize a FileProvider with the files in <filelist>.
        If len(filelist) is 1, a OrderedFileProvider will be constructed, which
        will simply open all files in the passed directory.
        If len(filelist) is greater 1, a PreDefinedFileProvider will be created,
        which will only ever list the files that were passed into it.
        If len(filelist) is zero, FileProvider will look at the last file opened,
        if "Auto Open last file" is set. Otherwise, no provider is constructed
        """

        if not filelist:
            return None
        elif len(filelist) == 1:
            return OrderedFileProvider(filelist[0])
        else:
            return PreDefinedFileProvider(filelist)
