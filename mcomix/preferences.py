# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

from pathlib import Path

from loguru import logger

from mcomix import constants
from mcomix.config import ConfigManager

# All preferences are stored here.
prefs = {
    'AUTO_OPEN_NEXT_ARCHIVE': True,
    'AUTO_OPEN_NEXT_DIRECTORY': False,
    'SORT_BY': constants.SORT_NAME,  # Normal files obtained by directory listing
    'SORT_ORDER': constants.SORT_ASCENDING,
    'SORT_ARCHIVE_BY': constants.SORT_NAME,  # Files in archives
    'SORT_ARCHIVE_ORDER': constants.SORT_ASCENDING,
    'CHECKERED_BG_FOR_TRANSPARENT_IMAGES': True,
    'STRETCH': True,
    'DEFAULT_DOUBLE_PAGE': True,
    'DEFAULT_FULLSCREEN': False,
    'ZOOM_MODE': constants.ZOOM_MODE_BEST,
    'DEFAULT_MANGA_MODE': True,
    'MANGA_FLIP_RIGHT': False,
    'LENS_MAGNIFICATION': 2,
    'LENS_SIZE': 200,
    'ENHANCE_EXTRA': True,
    'VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES': constants.SHOW_DOUBLE_AS_ONE_TITLE | constants.SHOW_DOUBLE_AS_ONE_WIDE,
    'DOUBLE_STEP_IN_DOUBLE_PAGE_MODE': True,
    'SHOW_PAGE_NUMBERS_ON_THUMBNAILS': True,
    'THUMBNAIL_SIZE': 80,
    'ARCHIVE_THUMBNAIL_AS_ICON': False,
    'PIXELS_TO_SCROLL_PER_KEY_EVENT': 50,
    'PIXELS_TO_SCROLL_PER_MOUSE_WHEEL_EVENT': 50,
    'FLIP_WITH_WHEEL': True,
    'HIDE_ALL': False,
    'HIDE_ALL_IN_FULLSCREEN': True,
    'SHOW_MENUBAR': True,
    'SHOW_SCROLLBAR': True,
    'SHOW_STATUSBAR': True,
    'SHOW_THUMBNAILS': True,
    'ROTATION': 0,
    'AUTO_ROTATE_FROM_EXIF': True,
    'AUTO_ROTATE_DEPENDING_ON_SIZE': constants.AUTOROTATE_NEVER,
    'VERTICAL_FLIP': False,
    'HORIZONTAL_FLIP': False,
    'KEEP_TRANSFORMATION': False,
    'STORED_DIALOG_CHOICES': {},
    'BRIGHTNESS': 1.0,
    'CONTRAST': 1.0,
    'SATURATION': 1.0,
    'SHARPNESS': 1.0,
    'AUTO_CONTRAST': False,
    'MAX_PAGES_TO_CACHE': -1,
    'STATUSBAR_FIELDS': constants.STATUS_PAGE | constants.STATUS_RESOLUTION | constants.STATUS_PATH | constants.STATUS_FILENAME | constants.STATUS_FILESIZE | constants.STATUS_MODE,
    'STATUSBAR_FULLPATH': True,
    'MAX_THREADS_THUMBNAIL': 16,
    'MAX_THREADS_EXTRACT': 16,
    'MAX_THREADS_GENERAL': 16,
    'SCALING_QUALITY': 2,  # GdkPixbuf.InterpType.BILINEAR
    'ESCAPE_QUITS': True,
    'FIT_TO_SIZE_MODE': constants.ZOOM_MODE_HEIGHT,
    'FIT_TO_SIZE_PX': 1800,
    'ANIMATION_MODE': constants.ANIMATION_INF,
    'ANIMATION_BACKGROUND': True,
    'ANIMATION_TRANSFORM': True,
    'MOVE_FILE': 'keep',
    'CHECK_IMAGE_MIMETYPE': False,
    'HIDE_CURSOR': False,
    'STATUSBAR_SPACING': 5,
    'OPEN_FIRST_PAGE': True,
    'WINDOW_SAVE': True,
    'WINDOW_X': 0,
    'WINDOW_Y': 0,
    'WINDOW_HEIGHT': 600,
    'WINDOW_WIDTH': 640,
    'BOOKMARK_WIDTH': 1300,
    'BOOKMARK_HEIGHT': 650,
    'PROPERTIES_WIDTH': 870,
    'PROPERTIES_HEIGHT': 560,
    'PROPERTIES_THUMB_SIZE': 256,
    'PAGESELECTOR_HEIGHT': 820,
    'PAGESELECTOR_WIDTH': 560,
}


class _PreferenceManager:
    def __init__(self):
        super().__init__()

        self.__preference_path = constants.PREFERENCE_PATH
        self.__prefs_hash = {'sha256': None}

    def load_preferences_file(self):
        saved_prefs = {}
        if Path.is_file(self.__preference_path):
            saved_prefs = ConfigManager.load_config(self.__preference_path, saved_prefs)

        prefs.update(filter(lambda i: i[0] in prefs, saved_prefs.items()))

        self.__prefs_hash['sha256'] = ConfigManager.hash_config(prefs)

    def write_preferences_file(self):
        sha256hash = ConfigManager.hash_config(prefs)
        if sha256hash == self.__prefs_hash['sha256']:
            logger.info('No changes to write for preferences')
            return
        self.__prefs_hash['sha256'] = sha256hash

        logger.info('Writing changes to preferences')

        ConfigManager.write_config(prefs, self.__preference_path)


# Singleton instance
PreferenceManager = _PreferenceManager()
