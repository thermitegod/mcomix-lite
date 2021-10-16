# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

from mcomix.constants import Constants
from mcomix.enum.animation import Animation
from mcomix.enum.config_files import ConfigPaths
from mcomix.enum.file_sort import FileSortDirection, FileSortType
from mcomix.enum.zoom_modes import ZoomModes

# All preferences are stored here.
config = {
    'AUTO_OPEN_NEXT_ARCHIVE': True,
    'SORT_BY': FileSortType.NAME.value,  # Normal files obtained by directory listing
    'SORT_ORDER': FileSortDirection.ASCENDING.value,
    'SORT_ARCHIVE_BY': FileSortType.NAME.value,  # Files in archives
    'SORT_ARCHIVE_ORDER': FileSortDirection.ASCENDING.value,
    'CHECKERED_BG_FOR_TRANSPARENT_IMAGES': True,
    'CHECKERED_BG_SIZE': 16,
    'STRETCH': True,
    'DEFAULT_DOUBLE_PAGE': True,
    'DEFAULT_FULLSCREEN': False,
    'FULLSCREEN_HIDE_MENUBAR': False,
    'FULLSCREEN_HIDE_STATUSBAR': False,
    'ZOOM_MODE': ZoomModes.BEST.value,
    'DEFAULT_MANGA_MODE': True,
    'MANGA_FLIP_RIGHT': False,
    'WESTERN_FLIP_LEFT': False,
    'PAGE_FF_STEP': 10,
    'LENS_MAGNIFICATION': 2,
    'LENS_SIZE': 200,
    'ENHANCE_EXTRA': True,
    'VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES': Constants.DOUBLE_PAGE['AS_ONE_TITLE'] |
                                              Constants.DOUBLE_PAGE['AS_ONE_WIDE'],
    'DOUBLE_STEP_IN_DOUBLE_PAGE_MODE': True,
    'SHOW_PAGE_NUMBERS_ON_THUMBNAILS': True,
    'THUMBNAIL_SIZE': 80,
    'PIXELS_TO_SCROLL_PER_KEY_EVENT': 50,
    'PIXELS_TO_SCROLL_PER_MOUSE_WHEEL_EVENT': 50,
    'FLIP_WITH_WHEEL': True,
    'FILECHOOSER_LAST_BROWSED_PATH': str(ConfigPaths.HOME.value),
    'FILECHOOSER_LAST_FILTER': 0,
    'ROTATION': 0,
    'AUTO_ROTATE_FROM_EXIF': True,
    'KEEP_TRANSFORMATION': False,
    'STORED_DIALOG_CHOICES': {},
    'BRIGHTNESS': 1.0,
    'CONTRAST': 1.0,
    'SATURATION': 1.0,
    'SHARPNESS': 1.0,
    'AUTO_CONTRAST': False,
    'PAGE_CACHE_FORWARD': 8,
    'PAGE_CACHE_BEHIND': 4,
    'STATUSBAR_FIELD_PAGE_NUMBERS': True,
    'STATUSBAR_FIELD_FILE_NUMBERS': True,
    'STATUSBAR_FIELD_PAGE_RESOLUTION': True,
    'STATUSBAR_FIELD_ARCHIVE_NAME': True,
    'STATUSBAR_FIELD_PAGE_FILENAME': True,
    'STATUSBAR_FIELD_PAGE_FILESIZE': True,
    'STATUSBAR_FIELD_ARCHIVE_FILESIZE': True,
    'STATUSBAR_FIELD_PAGE_SCALING': True,
    'STATUSBAR_FIELD_VIEW_MODE': True,
    'STATUSBAR_FULLPATH': True,
    'STATUSBAR_SEPARATOR': '|',
    'STATUSBAR_SHOW_SCALE': True,
    'STATUSBAR_MARGIN_PADDING': 2,
    'BOOKMARK_SHOW_PATH': False,
    'SI_UNITS': False,
    'MAX_THREADS': 16,
    'GDK_SCALING_FILTER': Constants.SCALING_GDK[2].value,
    'PIL_SCALING_FILTER': Constants.SCALING_PIL[2].value,
    'ENABLE_PIL_SCALING': True,
    'ESCAPE_QUITS': True,
    'FIT_TO_SIZE_MODE': ZoomModes.HEIGHT.value,
    'FIT_TO_SIZE_PX': 1800,
    'ANIMATION_MODE': Animation.INF.value,
    'ANIMATION_BACKGROUND': True,
    'ANIMATION_TRANSFORM': True,
    'MOVE_FILE': 'keep',
    'HIDE_CURSOR': False,
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
