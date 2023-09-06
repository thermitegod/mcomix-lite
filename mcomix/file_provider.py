# -*- coding: utf-8 -*-

from loguru import logger

from mcomix.providers.file_provider_ordered import OrderedFileProvider
from mcomix.providers.file_provider_predefined import PreDefinedFileProvider


class GetFileProvider:
    def __init__(self):
        super().__init__()

    def get_file_provider(self, filelist: list):
        """
        Initialize a FileProvider with the files in <filelist>.
        If len(filelist) is 1, a OrderedFileProvider will be constructed, which
        will simply open all files in the passed directory.
        If len(filelist) is greater 1, a PreDefinedFileProvider will be created,
        which will only ever list the files that were passed into it.
        """

        if len(filelist) == 1:
            # A single file was passed - use Comix' classic open mode
            # and open all files in its directory.
            logger.info('File provider: Ordered')
            return OrderedFileProvider(filelist[0])

        # A list of files was passed - open only these files.
        logger.info('File provider: Predefined')
        return PreDefinedFileProvider(filelist)
