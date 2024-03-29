# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# must not depend on GTK, or any other optional libraries.

from mcomix.enums import Animation, ConfigPaths, DoublePage, FileSortDirection, FileSortType, ZoomModes

# All preferences are stored here.
config = {
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
    'PAGE_FF_STEP': 10,
    'ENHANCE_EXTRA': True,
    'VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES': DoublePage.ALWAYS.value,
    'DOUBLE_STEP_IN_DOUBLE_PAGE_MODE': True,
    'SHOW_PAGE_NUMBERS_ON_THUMBNAILS': True,
    'THUMBNAIL_SIZE': 80,
    'PIXELS_TO_SCROLL_PER_KEY_EVENT': 50,
    'PIXELS_TO_SCROLL_PER_MOUSE_WHEEL_EVENT': 50,
    'FLIP_WITH_WHEEL': True,
    'FILECHOOSER_LAST_BROWSED_PATH': str(ConfigPaths.HOME.value),
    'FILECHOOSER_LAST_FILTER': 0,
    'ROTATION': 0,
    'KEEP_TRANSFORMATION': False,
    'STORED_DIALOG_CHOICES': {},
    'PAGE_CACHE_FORWARD': 3,
    'PAGE_CACHE_BEHIND': 2,
    'STATUSBAR_FIELD_PAGE_NUMBERS': True,
    'STATUSBAR_FIELD_FILE_NUMBERS': True,
    'STATUSBAR_FIELD_PAGE_RESOLUTION': True,
    'STATUSBAR_FIELD_ARCHIVE_NAME': True,
    'STATUSBAR_FIELD_PAGE_FILENAME': True,
    'STATUSBAR_FIELD_PAGE_FILESIZE': True,
    'STATUSBAR_FIELD_ARCHIVE_FILESIZE': True,
    'STATUSBAR_FIELD_VIEW_MODE': True,
    'STATUSBAR_FULLPATH': True,
    'STATUSBAR_SHOW_SCALE': True,
    'BOOKMARK_SHOW_PATH': False,
    'SI_UNITS': False,
    'MAX_THREADS': 16,
    'ESCAPE_QUITS': True,
    'FIT_TO_SIZE_MODE': ZoomModes.HEIGHT.value,
    'FIT_TO_SIZE_PX': 1800,
    'ANIMATION_MODE': Animation.NORMAL.value,
    'ANIMATION_BACKGROUND': True,
    'ANIMATION_TRANSFORM': True,
    'MOVE_FILE': 'keep',
    'OPEN_FIRST_PAGE': True,
    'WINDOW_SAVE': True,
    'WINDOW_X': 0,
    'WINDOW_Y': 0,
    'WINDOW_HEIGHT': 600,
    'WINDOW_WIDTH': 640,
    'BOOKMARK_WIDTH': 1300,
    'BOOKMARK_HEIGHT': 650,
}
