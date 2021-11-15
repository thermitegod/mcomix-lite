# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path

from loguru import logger

try:
    import gi
    gi.require_version('PangoCairo', '1.0')
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gdk, Gtk
except (ValueError, ImportError):
    raise SystemExit('GTK+ 3.0 import error')

from mcomix.enums import Mcomix


def main():
    parser = argparse.ArgumentParser(usage='%%(prog)s %s' % '[OPTION...] [PATH]',
                                     description='View images and manga archives.')
    parser.add_argument('path',
                        type=str,
                        action='store',
                        nargs='*',
                        default=None,
                        help=argparse.SUPPRESS)
    parser.add_argument('-v', '--version',
                        dest='version',
                        action='store_true',
                        help='Show the version number and exit.')
    debug = parser.add_argument_group('Debug options')
    debug.add_argument('-L', '--loglevel',
                       default='WARNING',
                       metavar='LEVEL',
                       type=str.upper,
                       choices=['NONE', 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'VERBOSE', 'DEBUG', 'TRACE'],
                       help='Levels: %(choices)s')
    args = parser.parse_args()

    if args.version:
        raise SystemExit(f'{Mcomix.APP_NAME.value} {Mcomix.VERSION.value}')

    # start logger
    logger.remove()
    logger.add(sys.stdout, level=args.loglevel, colorize=True)

    open_path = []
    for idx, item in enumerate(args.path):
        p = Path(item).resolve()
        if not Path.exists(p):
            logger.warning(f'File does not exist: \'{p}\'')
            continue
        logger.info(f'Loading file from command line: \'{p}\'')
        open_path.append(p)

    Gdk.set_program_class(Mcomix.APP_NAME.value)

    from mcomix.main_window import MainWindow
    window = MainWindow(open_path=open_path)

    try:
        Gtk.main()
    except KeyboardInterrupt:
        # Will not always work because of threading.
        window.terminate_program()
