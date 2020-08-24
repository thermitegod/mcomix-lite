# -*- coding: utf-8 -*-

"""icons.py - Load MComix specific icons"""

from importlib import resources

from gi.repository import Gtk
from loguru import logger

from mcomix import image_tools


def mcomix_icons():
    """
    Returns a list of differently sized pixbufs for the application icon
    """

    # not using resized since getting namespace errors
    pixbufs = [image_tools.load_pixbuf_data(resources.read_binary('mcomix.images', 'mcomix.png'))]
    return pixbufs


def load_icons():
    _icons = (('gimp-flip-horizontal.png', 'mcomix-flip-horizontal'),
              ('gimp-flip-vertical.png', 'mcomix-flip-vertical'),
              ('gimp-rotate-180.png', 'mcomix-rotate-180'),
              ('gimp-rotate-270.png', 'mcomix-rotate-270'),
              ('gimp-rotate-90.png', 'mcomix-rotate-90'),
              ('gimp-transform.png', 'mcomix-transform'),
              ('tango-enhance-image.png', 'mcomix-enhance-image'),
              ('tango-add-bookmark.png', 'mcomix-add-bookmark'),
              ('tango-archive.png', 'mcomix-archive'),
              ('tango-image.png', 'mcomix-image'),
              ('zoom.png', 'mcomix-zoom'),
              ('lens.png', 'mcomix-lens'))

    # Load window title icons.
    pixbufs = mcomix_icons()
    Gtk.Window.set_default_icon_list(pixbufs)

    # Load application icons.
    factory = Gtk.IconFactory()
    for filename, stockid in _icons:
        try:
            icon_data = resources.read_binary('mcomix.images', filename)
            pixbuf = image_tools.load_pixbuf_data(icon_data)
            iconset = Gtk.IconSet.new_from_pixbuf(pixbuf)
            factory.add(stockid, iconset)
        except Exception:
            logger.warning(f'Could not load icon: \'{filename}\'')
    factory.add_default()
