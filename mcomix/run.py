# -*- coding: utf-8 -*-

import argparse
import os
import signal
import sys

if __name__ == '__main__':
    print('PROGRAM TERMINATED\nDo not run this script directly, use mcomixstarter.py')
    sys.exit(1)

# These modules must not depend on GTK, PIL,
# or any other optional libraries.
from mcomix import constants, log, preferences


def parse_arguments():
    """Parse the command line passed in <argv>. Returns a tuple containing
    (options, arguments). Errors parsing the command line are handled in this function"""
    parser = argparse.ArgumentParser(usage='%%(prog)s %s' % '[OPTION...] [PATH]',
                                     description='View images and comic book archives.',
                                     add_help=False)
    parser.add_argument('--help', action='help',
                        help='Show this help and exit.')
    parser.add_argument('path', type=str, action='store', nargs='*', default='',
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
    fitmodes.add_argument('-w', '--zoom-width', dest='zoommode', action='store_const',
                          const=constants.ZOOM_MODE_WIDTH,
                          help='Start the application with zoom set to fit width.')
    fitmodes.add_argument('-h', '--zoom-height', dest='zoommode', action='store_const',
                          const=constants.ZOOM_MODE_HEIGHT,
                          help='Start the application with zoom set to fit height.')

    debugopts = parser.add_argument_group('Debug options')
    debugopts.add_argument('-W', dest='loglevel', action='store',
                           choices=log.levels.keys(), default='warn',
                           metavar='[ {} ]'.format(' | '.join(log.levels.keys())),
                           help='Sets the desired output log level.')
    # This supresses an error when MComix is used with cProfile
    debugopts.add_argument('-o', dest='output', action='store',
                           default='', help=argparse.SUPPRESS)

    args = parser.parse_args()

    return args


def run():
    """Run the program"""
    # Load configuration.
    preferences.read_preferences_file()

    # Retrieve and parse command line arguments.
    args = parse_arguments()

    if args.version:
        print(constants.APPNAME + ' ' + constants.VERSION)
        sys.exit(0)

    # First things first: set the log level.
    log.setLevel(log.levels[args.loglevel])

    # Check for PyGTK and PIL dependencies.
    try:
        from gi import version_info as gi_version_info
        assert gi_version_info >= (3, 21, 0)

        from gi import require_version

        require_version('PangoCairo', '1.0')
        require_version('Gtk', '3.0')
        require_version('Gdk', '3.0')

        from gi.repository import Gdk, Gtk, GLib

    except AssertionError:
        log.error('Required versions of PyGObject is not installed.')
        sys.exit(1)

    except ValueError:
        log.error('Required versions of GTK+ 3.0 is not installed.')
        sys.exit(1)

    except ImportError:
        log.error('No version of GObject was found.')
        sys.exit(1)

    try:
        import PIL.Image
        pilver = getattr(PIL.Image, '__version__', None)
        assert pilver >= constants.REQUIRED_PIL_VERSION

    except (AssertionError, AttributeError):
        log.error('Required version of Pillow is not installed.')
        log.error('Required version is at least %s' % constants.REQUIRED_PIL_VERSION)
        sys.exit(1)

    except ImportError:
        log.error('No version of Pillow was found.')
        sys.exit(1)

    try:
        import numpy

    except ImportError:
        log.error('No version of Numpy was found.')
        sys.exit(1)

    if not os.path.exists(constants.DATA_DIR):
        os.makedirs(constants.DATA_DIR, 0o700)

    if not os.path.exists(constants.CONFIG_DIR):
        os.makedirs(constants.CONFIG_DIR, 0o700)

    from mcomix import icons
    icons.load_icons()

    open_path = args.path or None
    open_page = 1

    if isinstance(open_path, list):
        n = 0
        while n < len(open_path):
            p = os.path.join(os.getcwd(), open_path[n])
            p = os.path.normpath(p)
            if not os.path.exists(p):
                log.error('Non existant file: {}'.format(p))
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
    main.set_main_window(window)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, stack: GLib.idle_add(window.terminate_program))
    try:
        Gtk.main()
    except KeyboardInterrupt:  # Will not always work because of threading.
        window.terminate_program()
