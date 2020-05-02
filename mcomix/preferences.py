# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

import json
from pathlib import Path

from loguru import logger

from mcomix import constants, tools

# All preferences are stored here.
prefs = {
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
    'archive thumbnail as icon': False,
    'number of pixels to scroll per key event': 50,
    'number of pixels to scroll per mouse wheel event': 50,
    'flip with wheel': True,
    'hide all': False,
    'hide all in fullscreen': True,
    'show menubar': True,
    'show scrollbar': True,
    'show statusbar': True,
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
    'max pages to cache': -1,
    'statusbar fields': constants.STATUS_PAGE | constants.STATUS_RESOLUTION | constants.STATUS_PATH | constants.STATUS_FILENAME | constants.STATUS_FILESIZE,
    'max thumbnail threads': 16,
    'max extract threads': 16,
    'scaling quality': 2,  # GdkPixbuf.InterpType.BILINEAR
    'escape quits': True,
    'fit to size mode': constants.ZOOM_MODE_HEIGHT,
    'fit to size px': 1800,
    'external commands': [],  # (label, command) pairs
    'animation mode': constants.ANIMATION_INF,
    'animation background': True,
    'animation transform': True,
    'temporary directory': '/tmp',
    'move file': 'keep',
    'check image mimetype': False,
    'hide cursor': False,
    'statusbar spacing': 5,
    'window save': True,
    'window x': 0,
    'window y': 0,
    'window height': 600,
    'window width': 640,
    'bookmark width': 1300,
    'bookmark height': 650,
    'properties width': 870,
    'properties height': 560,
    'properties thumb size': 256,
    'pageselector height': 820,
    'pageselector width': 560,
}


class _PreferenceManager:
    def __init__(self):
        self.__preference_path = constants.PREFERENCE_PATH
        self.__prefs_hash = {'sha256': None}

    def load_preferences_file(self):
        saved_prefs = {}
        if Path.is_file(self.__preference_path):
            try:
                with Path.open(self.__preference_path, mode='rt', encoding='utf8') as fd:
                    saved_prefs.update(json.load(fd))
            except Exception:
                logger.error('Preferences file is corrupt')
                import sys
                sys.exit(1)

        prefs.update(filter(lambda i: i[0] in prefs, saved_prefs.items()))

        self.__prefs_hash['sha256'] = tools.sha256str(json.dumps(prefs, indent=2))

    def write_preferences_file(self):
        """Write preference data to disk"""
        json_prefs = json.dumps(prefs, indent=2)
        sha256hash = tools.sha256str(json_prefs)
        if sha256hash == self.__prefs_hash['sha256']:
            logger.info('No changes to write for preferences')
            return
        self.__prefs_hash['sha256'] = sha256hash

        logger.info('Writing changes to preferences')

        Path(self.__preference_path).write_text(json_prefs)


# Singleton instance
PreferenceManager = _PreferenceManager()
