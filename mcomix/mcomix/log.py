# -*- coding: utf-8 -*-

"""Logging module for MComix. Provides a logger 'mcomix' with a few
pre-configured settings. Functions in this module are redirected to
this default logger"""

import logging

from logging import DEBUG, INFO, WARNING, ERROR


__all__ = ['debug', 'info', 'warning', 'error', 'setLevel',
           'DEBUG', 'INFO', 'WARNING', 'ERROR']


class PrintHandler(logging.Handler):
    def __init__(self):
        super(PrintHandler, self).__init__()

    def emit(self, record):
        print(self.format(record))


# Set up default logger.
__logger = logging.getLogger('mcomix')
__logger.setLevel(WARNING)
if not __logger.handlers:
    __handler = PrintHandler()
    __handler.setFormatter(logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s', '%H:%M:%S'))
    __logger.handlers = [__handler]

# The following functions direct all input to __logger.
info = __logger.info
error = __logger.error
debug = __logger.debug
warning = __logger.warning
setLevel = __logger.setLevel
