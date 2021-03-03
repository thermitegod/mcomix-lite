# -*- coding: utf-8 -*-

# must not depend on GTK, PIL, or any other optional libraries.

from mcomix.constants import Constants

# All preferences are stored here.
config = {
    'AUTO_OPEN_NEXT_ARCHIVE': True,
    'SORT_BY': Constants.FILE_SORT_TYPE['NAME'],  # Normal files obtained by directory listing
    'SORT_ORDER': Constants.FILE_SORT_DIRECTION['ASCENDING'],
    'SORT_ARCHIVE_BY': Constants.FILE_SORT_TYPE['NAME'],  # Files in archives
    'SORT_ARCHIVE_ORDER': Constants.FILE_SORT_DIRECTION['ASCENDING'],
    'CHECKERED_BG_FOR_TRANSPARENT_IMAGES': True,
    'CHECKERED_BG_SIZE': 16,
    'STRETCH': True,
    'DEFAULT_DOUBLE_PAGE': True,
    'DEFAULT_FULLSCREEN': False,
    'ZOOM_MODE': Constants.ZOOM['BEST'],
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
    'ARCHIVE_THUMBNAIL_AS_ICON': False,
    'PIXELS_TO_SCROLL_PER_KEY_EVENT': 50,
    'PIXELS_TO_SCROLL_PER_MOUSE_WHEEL_EVENT': 50,
    'FLIP_WITH_WHEEL': True,
    'HIDE_ALL': False,
    'HIDE_ALL_IN_FULLSCREEN': True,
    'FILECHOOSER_LAST_BROWSED_PATH': Constants.HOME,
    'FILECHOOSER_LAST_FILTER': 0,
    'SHOW_MENUBAR': True,
    'SHOW_STATUSBAR': True,
    'SHOW_THUMBNAILS': True,
    'ROTATION': 0,
    'AUTO_ROTATE_FROM_EXIF': True,
    'AUTO_ROTATE_DEPENDING_ON_SIZE': Constants.AUTOROTATE['NEVER'],
    'VERTICAL_FLIP': False,
    'HORIZONTAL_FLIP': False,
    'KEEP_TRANSFORMATION': False,
    'STORED_DIALOG_CHOICES': {},
    'BRIGHTNESS': 1.0,
    'CONTRAST': 1.0,
    'SATURATION': 1.0,
    'SHARPNESS': 1.0,
    'AUTO_CONTRAST': False,
    'MAX_PAGES_TO_CACHE': 16,
    'STATUSBAR_FIELDS': Constants.STATUSBAR['PAGE_NUMBERS'] | Constants.STATUSBAR['PAGE_RESOLUTION'] |
                        Constants.STATUSBAR['ARCHIVE_NAME'] | Constants.STATUSBAR['PAGE_FILENAME'] |
                        Constants.STATUSBAR['FILE_NUMBERS'] | Constants.STATUSBAR['PAGE_FILESIZE'] |
                        Constants.STATUSBAR['ARCHIVE_FILESIZE'] | Constants.STATUSBAR['VIEW_MODE'],
    'STATUSBAR_FULLPATH': True,
    'STATUSBAR_SEPARATOR': '|',
    'STATUSBAR_SHOW_SCALE': True,
    'BOOKMARK_SHOW_PATH': False,
    'SI_UNITS': False,
    'MAX_THREADS': 16,
    'SCALING_QUALITY': 2,  # GdkPixbuf.InterpType.BILINEAR
    'PIL_SCALING_FILTER': 1,  # PIL filter in main viewing area. -1 to just use GdkPixbuf
    'ESCAPE_QUITS': True,
    'FIT_TO_SIZE_MODE': Constants.ZOOM['HEIGHT'],
    'FIT_TO_SIZE_PX': 1800,
    'ANIMATION_MODE': Constants.ANIMATION['INF'],
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
