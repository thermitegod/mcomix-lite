# -*- coding: utf-8 -*-

import json
import os

from mcomix import constants

# All preferences are stored here.
prefs = {
    'comment extensions': constants.ACCEPTED_COMMENT_EXTENSIONS,
    'auto load last file': False,
    'page of last file': 1,
    'path to last file': '',
    'number of key presses before page turn': 3,
    'auto open next archive': True,
    'auto open next directory': False,
    'sort by': constants.SORT_NAME,  # Normal files obtained by directory listing
    'sort order': constants.SORT_ASCENDING,
    'sort archive by': constants.SORT_NAME,  # Files in archives
    'sort archive order': constants.SORT_ASCENDING,
    'bg color': [0, 0, 0, 0],
    'thumb bg color': [0, 0, 0, 0],
    'thumbnail bg uses main color': False,
    'checkered bg for transparent images': True,
    'cache': True,
    'stretch': True,
    'default double page': True,
    'default fullscreen': False,
    'zoom mode': constants.ZOOM_MODE_BEST,
    'default manga mode': True,
    'lens magnification': 2,
    'lens size': 200,
    'virtual double page for fitting images': constants.SHOW_DOUBLE_AS_ONE_TITLE | constants.SHOW_DOUBLE_AS_ONE_WIDE,
    'double step in double page mode': True,
    'show page numbers on thumbnails': True,
    'thumbnail size': 80,
    'create thumbnails': True,
    'archive thumbnail as icon': False,
    'number of pixels to scroll per key event': 50,
    'number of pixels to scroll per mouse wheel event': 50,
    'slideshow delay': 3000,
    'slideshow can go to next archive': True,
    'number of pixels to scroll per slideshow event': 50,
    'smart scroll': True,
    'invert smart scroll': True,
    'smart scroll percentage': 0.5,
    'flip with wheel': True,
    'store recent file info': False,
    'hide all': False,
    'hide all in fullscreen': True,
    'stored hide all values': [True, True, True, True, True],
    'path of last browsed in filechooser': constants.HOME_DIR,
    'last filter in main filechooser': 0,
    'last filter in library filechooser': 1,
    'show menubar': True,
    'previous quit was quit and save': False,
    'show scrollbar': True,
    'show statusbar': True,
    'show toolbar': False,
    'show thumbnails': True,
    'rotation': 0,
    'auto rotate from exif': True,
    'auto rotate depending on size': constants.AUTOROTATE_NEVER,
    'vertical flip': False,
    'horizontal flip': False,
    'keep transformation': False,
    'stored dialog choices': {},
    'brightness': 1.0,
    'contrast': 1.0,
    'saturation': 1.0,
    'sharpness': 1.0,
    'auto contrast': False,
    'max pages to cache': 9,
    'window x': 0,
    'window y': 0,
    'window height': 600,
    'window width': 640,
    'pageselector height': -1,
    'pageselector width': -1,
    'library cover size': 125,
    'last library collection': None,
    'lib window height': 600,
    'lib window width': 500,
    'lib sort key': constants.SORT_PATH,
    'lib sort order': constants.SORT_ASCENDING,
    'statusbar fields': constants.STATUS_PAGE | constants.STATUS_RESOLUTION | \
                        constants.STATUS_PATH | constants.STATUS_FILENAME | constants.STATUS_FILESIZE,
    'max threads': 32,
    'max extract threads': 16,
    'wrap mouse scroll': False,
    'scaling quality': 3,  # GdkPixbuf.InterpType.HYPER
    'escape quits': True,
    'fit to size mode': constants.ZOOM_MODE_HEIGHT,
    'fit to size px': 1800,
    'scan for new books on library startup': False,
    'openwith commands': [],  # (label, command) pairs
    'animation mode': constants.ANIMATION_INF,
    'animation background': True,
    'animation transform': True,
    'temporary directory': None,
}


def read_preferences_file():
    saved_prefs = None

    if os.path.isfile(constants.PREFERENCE_PATH):
        try:
            with open(constants.PREFERENCE_PATH, 'r') as config_file:
                saved_prefs = json.load(config_file)
        except:
            corrupt_name = '%s.broken' % constants.PREFERENCE_PATH
            print('! Corrupt preferences file, moving to "%s".' % corrupt_name)
            if os.path.isfile(corrupt_name):
                os.unlink(corrupt_name)

            os.rename(constants.PREFERENCE_PATH, corrupt_name)

    if saved_prefs:
        for key in saved_prefs:
            if key in prefs:
                prefs[key] = saved_prefs[key]


def write_preferences_file():
    """Write preference data to disk."""
    with open(constants.PREFERENCE_PATH, 'w') as config_file:
        json.dump(prefs, config_file, indent=2)
