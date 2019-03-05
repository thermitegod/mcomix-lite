# -*- coding: utf-8 -*-

import argparse
import os
import signal
import sys

if __name__ == '__main__':
    print('PROGRAM TERMINATED')
    print('Do not run this script directly, instead use mcomixstarter.py.')
    sys.exit(1)

# These modules must not depend on GTK, PIL,
# or any other optional libraries.
from mcomix import constants, log, preferences


def print_version():
    """Print the version number and exit."""
    print(constants.APPNAME + ' ' + constants.VERSION)
    sys.exit(0)


def parse_arguments():
    """ Parse the command line passed in <argv>. Returns a tuple containing
    (options, arguments). Errors parsing the command line are handled in
    this function. """

    parser = argparse.ArgumentParser(
        usage="%%(prog)s %s" % '[OPTION...] [PATH]',
        description='View images and comic book archives.',
        add_help=False)
    parser.add_argument('--help', action='help',
                        help='Show this help and exit.')
    parser.add_argument("path", type=str, action='store', nargs='*', default='',
                        help=argparse.SUPPRESS)

    parser.add_argument('-s', '--slideshow', dest='slideshow', action='store_true',
                        help='Start the application in slideshow mode.')
    parser.add_argument('-l', '--library', dest='library', action='store_true',
                        help='Show the library on startup.')
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
                           choices=('all', 'debug', 'info', 'warn', 'error'), default='warn',
                           metavar='[ all | debug | info | warn | error ]',
                           help='Sets the desired output log level.')
    # This supresses an error when MComix is used with cProfile
    debugopts.add_argument('-o', dest='output', action='store',
                           default='', help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Fix up log level to use constants from log.
    if args.loglevel == 'all':
        args.loglevel = log.DEBUG
    if args.loglevel == 'debug':
        args.loglevel = log.DEBUG
    if args.loglevel == 'info':
        args.loglevel = log.INFO
    elif args.loglevel == 'warn':
        args.loglevel = log.WARNING
    elif args.loglevel == 'error':
        args.loglevel = log.ERROR

    return args


def run():
    """Run the program."""

    # Load configuration and setup localisation.
    preferences.read_preferences_file()

    # Retrieve and parse command line arguments.
    args = parse_arguments()

    if args.version:
        print_version()

    # First things first: set the log level.
    log.setLevel(args.loglevel)

    # Check for PyGTK and PIL dependencies.
    try:
        from gi import require_version

        require_version('PangoCairo', '1.0')
        require_version('Gtk', '3.0')
        require_version('Gdk', '3.0')

        from gi.repository import Gdk, Gtk, GLib
        from gi import version_info as gi_version_info

        if gi_version_info < (3, 11, 0):
            from gi.repository import GObject
            GObject.threads_init()

    except AssertionError:
        log.error('You do not have the required versions of GTK+ 3.0 and PyGObject installed.')
        sys.exit(1)

    except ImportError:
        log.error('No version of GObject was found on your system.')
        sys.exit(1)

    try:
        # FIXME
        # check Pillow version carefully here.
        # from 5.1.0 to 5.4.1, PILLOW_VERSION is used,
        # but since 6.0.0, only __version__ should be used.
        # clean up these code once python 3.6 goes EOL (maybe 2021)
        # (https://pillow.readthedocs.io/en/stable/releasenotes/5.2.0.html)
        import PIL.Image
        pilver = getattr(PIL.Image, '__version__', None)
        if not pilver:
            pilver = getattr(PIL.Image, 'PILLOW_VERSION')
        assert pilver >= constants.REQUIRED_PIL_VERSION

    except (AssertionError, AttributeError):
        log.error('You do not have the required version of Pillow installed.')
        log.error('Installed Pillow version is: %s' % pilver)
        log.error('Required Pillow version is: %s or higher' % constants.REQUIRED_PIL_VERSION)
        sys.exit(1)

    except ImportError:
        log.error('Pillow version %s or higher is required.' % constants.REQUIRED_PIL_VERSION)
        log.error('No version of Pillow was found on your system.')
        sys.exit(1)

    try:
        import numpy

    except ImportError:
        log.error('No version of Numpy was found on your system.')
        sys.exit(1)

    try:
        import sqlite3

    except ImportError:
        log.error('Python not build with sqlite support.')
        sys.exit(1)

    if not os.path.exists(constants.DATA_DIR):
        os.makedirs(constants.DATA_DIR, 0o700)

    if not os.path.exists(constants.CONFIG_DIR):
        os.makedirs(constants.CONFIG_DIR, 0o700)

    from mcomix import icons
    icons.load_icons()

    open_path = args.path or None
    open_page = 1

    if not open_path and preferences.prefs['auto load last file'] \
            and preferences.prefs['path to last file'] \
            and os.path.isfile(preferences.prefs['path to last file']):
        open_path = preferences.prefs['path to last file']
        open_page = preferences.prefs['page of last file']

    Gdk.set_program_class(constants.APPNAME)

    settings = Gtk.Settings.get_default()
    # Enable icons for menu items.
    settings.props.gtk_menu_images = True

    from mcomix import main
    window = main.MainWindow(fullscreen=args.fullscreen, is_slideshow=args.slideshow,
                             show_library=args.library, manga_mode=args.manga,
                             double_page=args.doublepage, zoom_mode=args.zoommode,
                             open_path=open_path, open_page=open_page)
    main.set_main_window(window)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, stack: GLib.idle_add(window.terminate_program))
    try:
        Gtk.main()
    except KeyboardInterrupt:  # Will not always work because of threading.
        window.terminate_program()
