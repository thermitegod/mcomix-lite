# -*- coding: utf-8 -*-

# Do not run this script directly, use mcomixstarter.py

import argparse
import signal
import sys
from pathlib import Path

from loguru import logger

from mcomix import constants, preferences


def run():
    """Run the program"""
    parser = argparse.ArgumentParser(usage='%%(prog)s %s' % '[OPTION...] [PATH]',
                                     description='View images and manga archives.')
    parser.add_argument('path', type=str, action='store', nargs='*', default=None,
                        help=argparse.SUPPRESS)
    parser.add_argument('-v', '--version', dest='version', action='store_true',
                        help='Show the version number and exit.')
    viewmodes = parser.add_argument_group('View modes')
    viewmodes.add_argument('-f', '--fullscreen', dest='fullscreen', action='store_true',
                           help='Start the application in fullscreen mode.')
    viewmodes.add_argument('-m', '--manga', dest='manga', action='store_true',
                           help='Start the application in manga mode.')
    viewmodes.add_argument('-d', '--double-page', dest='doublepage', action='store_true',
                           help='Start the application in double page mode.')
    fitmodes = parser.add_argument_group('Zoom modes')
    fitmodes.add_argument('-b', '--zoom-best', dest='zoommode', action='store_const',
                          const=constants.ZOOM_MODE_BEST,
                          help='Start the application with zoom set to best fit mode.')
    fitmodes.add_argument('-zw', '--zoom-width', dest='zoommode', action='store_const',
                          const=constants.ZOOM_MODE_WIDTH,
                          help='Start the application with zoom set to fit width.')
    fitmodes.add_argument('-zh', '--zoom-height', dest='zoommode', action='store_const',
                          const=constants.ZOOM_MODE_HEIGHT,
                          help='Start the application with zoom set to fit height.')
    debugopts = parser.add_argument_group('Debug options')
    debugopts.add_argument('-L', '--loglevel', default='WARNING', metavar='LEVEL', type=str.upper,
                           choices=['NONE', 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'VERBOSE', 'DEBUG', 'TRACE'],
                           help='Levels: %(choices)s')
    args = parser.parse_args()

    if args.version:
        print(f'{constants.APPNAME} {constants.VERSION}')
        raise SystemExit

    # start logger
    logger.remove()
    logger.add(sys.stdout, level=args.loglevel, colorize=True)

    # Check for PyGTK and PIL dependencies.
    try:
        from gi import version_info, require_version
        assert version_info >= (3, 24, 0)

        require_version('PangoCairo', '1.0')
        require_version('Gtk', '3.0')
        require_version('Gdk', '3.0')

        from gi.repository import GLib, Gdk, GdkPixbuf, Gtk

    except (ValueError, AssertionError, ImportError):
        logger.error('GTK+ 3.0 import error.')
        raise SystemExit(1)

    try:
        import PIL.Image
        pilver = getattr(PIL.Image, '__version__', None)
        assert pilver >= constants.REQUIRED_PIL_VERSION

    except (AssertionError, AttributeError, ImportError):
        logger.error('Required version of Pillow is not installed. \n'
                     f'Required version is at least {constants.REQUIRED_PIL_VERSION}')
        raise SystemExit(1)

    logger.info(f'Image loaders: Pillow [{PIL.Image.__version__}], GDK [{GdkPixbuf.PIXBUF_VERSION}])')

    if not Path.exists(constants.DATA_DIR):
        constants.DATA_DIR.mkdir()

    if not Path.exists(constants.CONFIG_DIR):
        constants.CONFIG_DIR.mkdir()

    # Load configuration.
    preferences.PreferenceManager.load_preferences_file()

    from mcomix import icons
    icons.load_icons()

    open_path = args.path
    open_page = 1

    if isinstance(open_path, list):
        n = 0
        while n < len(open_path):
            p = Path() / open_path[n]
            if not Path.exists(p):
                logger.error(f'Non existant file: \'{p}\'')
                open_path.pop(n)
                continue
            open_path[n] = p
            n += 1
        if not open_path:
            open_path = None

    Gdk.set_program_class(constants.APPNAME)

    settings = Gtk.Settings.get_default()
    # Enable icons for menu items.
    settings.props.gtk_menu_images = True

    from mcomix import main
    window = main.MainWindow(fullscreen=args.fullscreen, manga_mode=args.manga,
                             double_page=args.doublepage, zoom_mode=args.zoommode,
                             open_path=open_path, open_page=open_page)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, stack: GLib.idle_add(window.terminate_program))
    try:
        Gtk.main()
    except KeyboardInterrupt:  # Will not always work because of threading.
        window.terminate_program()
