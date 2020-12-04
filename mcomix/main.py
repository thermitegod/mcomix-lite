# -*- coding: utf-8 -*-

# Do not run this script directly, use mcomixstarter.py

import argparse
import sys
from pathlib import Path

from mcomix.constants import Constants


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
        print(Constants.APPNAME, Constants.VERSION)
        raise SystemExit

    # start logger
    from loguru import logger
    logger.remove()
    logger.add(sys.stdout, level=args.loglevel, colorize=True)

    # Check for PyGTK and PIL dependencies.
    try:
        from gi import version_info, require_version

        if version_info < (3, 24, 0):
            raise ImportError

        require_version('PangoCairo', '1.0')
        require_version('Gtk', '3.0')
        require_version('Gdk', '3.0')

        from gi.repository import GLib, Gdk, GdkPixbuf, Gtk

    except (ValueError, ImportError):
        logger.critical('GTK+ 3.0 import error')
        raise SystemExit(1)

    try:
        import PIL
        pil_version = PIL.__version__

        if pil_version < Constants.REQUIRED_PIL_VERSION:
            raise ImportError

    except (AttributeError, ImportError):
        logger.critical(f'Required Pillow version is at least {Constants.REQUIRED_PIL_VERSION}')
        raise SystemExit(1)

    logger.info(f'Image loaders: Pillow [{pil_version}], GDK [{GdkPixbuf.PIXBUF_VERSION}]')

    # Load configuration.
    from mcomix.preferences_manager import PreferenceManager
    PreferenceManager.load_preferences_file()

    from mcomix.icons import Icons
    Icons.load_icons()

    open_path = []
    for idx, item in enumerate(args.path):
        p = Path(item).resolve()
        if not Path.exists(p):
            logger.warning(f'File does not exist: \'{p}\'')
            continue
        logger.info(f'Loading file from command line: \'{p}\'')
        open_path.append(p)

    if not open_path:
        open_path = None

    Gdk.set_program_class(Constants.APPNAME)

    settings = Gtk.Settings.get_default()
    # Enable icons for menu items.
    settings.props.gtk_menu_images = True

    from mcomix.main_window import MainWindow
    window = MainWindow(open_path=open_path)

    try:
        Gtk.main()
    except KeyboardInterrupt:
        # Will not always work because of threading.
        window.terminate_program()
