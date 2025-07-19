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

#: Bindings defined in this dictionary will appear in the configuration dialog.
#: If 'group' is None, the binding cannot be modified from the preferences dialog.

from dataclasses import dataclass
from typing import Callable

from mcomix.lib.events import Events, EventType
from mcomix.lib.metaclass import SingleInstanceMetaClass
from mcomix.preferences import config

from mcomix_compiled import ZoomModes


class KeyBindingsMap(metaclass=SingleInstanceMetaClass):
    def __init__(self):
        super().__init__()

        events = Events()

        group_nav = 'Navigation'
        group_scroll = 'Scrolling'
        group_zoom = 'Zoom'
        group_trans = 'Transformation'
        group_view = 'View mode'
        group_pagefit = 'Page fit mode'
        group_ui = 'User interface'
        group_info = 'Info'
        group_file = 'File'
        group_scale = 'Image Scaling'

        @dataclass(frozen=True)
        class INFO:
            group: str
            title: str

        @dataclass(frozen=True)
        class KEYBINDINGS:
            keybindings: list

        @dataclass(frozen=True)
        class KEY_EVENT:
            event: Callable
            event_type: EventType
            event_kwargs: dict

        @dataclass(frozen=True)
        class MAP:
            info: INFO
            keybindings: KEYBINDINGS
            key_event: KEY_EVENT

        self.__bindings = {
            # Navigation
            'previous_page':
                MAP(
                    INFO(group_nav, 'Previous page'),
                    KEYBINDINGS(['Up', 'Page_Up', 'KP_Page_Up']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_PAGE_FLIP,
                        {'number_of_pages': -1},
                    ),
                ),
            'next_page':
                MAP(
                    INFO(group_nav, 'Next page'),
                    KEYBINDINGS(['Down', 'Page_Down', 'KP_Page_Down']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_PAGE_FLIP,
                        {'number_of_pages': 1},
                    ),
                ),
            'previous_page_singlestep':
                MAP(
                    INFO(group_nav, 'Previous page (always one page)'),
                    KEYBINDINGS(['<Primary>Up', '<Primary>Page_Up', '<Primary>KP_Page_Up']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_PAGE_FLIP,
                        {'number_of_pages': -1, 'single_step': True},
                    ),
                ),
            'next_page_singlestep':
                MAP(
                    INFO(group_nav, 'Next page (always one page)'),
                    KEYBINDINGS(['<Primary>Down', '<Primary>Page_Down', '<Primary>KP_Page_Down']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_PAGE_FLIP,
                        {'number_of_pages': 1, 'single_step': True},
                    ),
                ),
            'previous_page_ff':
                MAP(
                    INFO(group_nav, 'Rewind by X pages'),
                    KEYBINDINGS(['<Shift>Page_Up', '<Shift>KP_Page_Up', '<Shift>BackSpace', '<Shift><Mod1>Left']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_PAGE_FLIP,
                        {'number_of_pages': -config['PAGE_FF_STEP']},
                    ),
                ),
            'next_page_ff':
                MAP(
                    INFO(group_nav, 'Forward by X pages'),
                    KEYBINDINGS(['<Shift>Page_Down', '<Shift>KP_Page_Down', '<Shift><Mod1>Right']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_PAGE_FLIP,
                        {'number_of_pages': config['PAGE_FF_STEP']},
                    ),
                ),
            'first_page':
                MAP(
                    INFO(group_nav, 'First page'),
                    KEYBINDINGS(['Home', 'KP_Home']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_PAGE_FIRST,
                        None,
                    ),
                ),
            'last_page':
                MAP(
                    INFO(group_nav, 'Last page'),
                    KEYBINDINGS(['End', 'KP_End']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_PAGE_LAST,
                        None,
                    ),
                ),
            'go_to':
                MAP(
                    INFO(group_nav, 'Go to page'),
                    KEYBINDINGS(['G']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_OPEN_PAGESELECTOR,
                        None,
                    ),
                ),
            'next_archive':
                MAP(
                    INFO(group_nav, 'Next archive'),
                    KEYBINDINGS(['<Primary>Right']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_OPEN_ARCHIVE_DIRECTION,
                        {'forward': True},
                    ),
                ),
            'previous_archive':
                MAP(
                    INFO(group_nav, 'Previous archive'),
                    KEYBINDINGS(['<Primary>Left']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_OPEN_ARCHIVE_DIRECTION,
                        {'forward': False},
                    ),
                ),

            # Scrolling
            # Arrow keys scroll the image
            'scroll_down':
                MAP(
                    INFO(group_scroll, 'Scroll down'),
                    KEYBINDINGS(['Down', 'KP_Down']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_SCROLL_WITH_FLIPPING,
                        {'x': 0, 'y': config['PIXELS_TO_SCROLL_PER_KEY_EVENT']},
                    ),
                ),
            'scroll_left':
                MAP(
                    INFO(group_scroll, 'Scroll left'),
                    KEYBINDINGS(['Left', 'KP_Left']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_SCROLL_WITH_FLIPPING,
                        {'x': -config['PIXELS_TO_SCROLL_PER_KEY_EVENT'], 'y': 0},
                    ),
                ),
            'scroll_right':
                MAP(
                    INFO(group_scroll, 'Scroll right'),
                    KEYBINDINGS(['Right', 'KP_Right']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_SCROLL_WITH_FLIPPING,
                        {'x': config['PIXELS_TO_SCROLL_PER_KEY_EVENT'], 'y': 0},
                    ),
                ),
            'scroll_up':
                MAP(
                    INFO(group_scroll, 'Scroll up'),
                    KEYBINDINGS(['Up', 'KP_Up']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_SCROLL_WITH_FLIPPING,
                        {'x': 0, 'y': -config['PIXELS_TO_SCROLL_PER_KEY_EVENT']},
                    ),
                ),

            # View
            'zoom_original':
                MAP(
                    INFO(group_zoom, 'Normal size'),
                    KEYBINDINGS(['<Control>0', 'KP_0']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_ZOOM_ORIGINAL,
                        None,
                    ),
                ),
            'zoom_in':
                MAP(
                    INFO(group_zoom, 'Zoom in'),
                    KEYBINDINGS(['plus', 'KP_Add', 'equal']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_ZOOM_IN,
                        None,
                    ),
                ),
            'zoom_out':
                MAP(
                    INFO(group_zoom, 'Zoom out'),
                    KEYBINDINGS(['minus', 'KP_Subtract']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_ZOOM_OUT,
                        None,
                    ),
                ),

            # Zoom out is already defined as GTK menu hotkey
            'keep_transformation':
                MAP(
                    INFO(group_trans, 'Keep transformation'),
                    KEYBINDINGS(['k']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_CHANGE_KEEP_TRANSFORMATION,
                        None,
                    ),
                ),
            'rotate_90':
                MAP(
                    INFO(group_trans, 'Rotate 90°'),
                    KEYBINDINGS(['r']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_PAGE_ROTATE,
                        {'rotation': 90},
                    ),
                ),
            'rotate_180':
                MAP(
                    INFO(group_trans, 'Rotate 180°'),
                    KEYBINDINGS([]),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_PAGE_ROTATE,
                        {'rotation': 180},
                    ),
                ),
            'rotate_270':
                MAP(
                    INFO(group_trans, 'Rotate 270°'),
                    KEYBINDINGS(['<Shift>r']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_PAGE_ROTATE,
                        {'rotation': 270},
                    ),
                ),

            # View mode
            'double_page':
                MAP(
                    INFO(group_view, 'Double page mode'),
                    KEYBINDINGS(['d']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_CHANGE_DOUBLE,
                        None,
                    ),
                ),
            'manga_mode':
                MAP(
                    INFO(group_view, 'Manga mode'),
                    KEYBINDINGS(['m']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_CHANGE_MANGA,
                        None,
                    ),
                ),

            # Fit mode
            'stretch':
                MAP(
                    INFO(group_pagefit, 'Stretch small images'),
                    KEYBINDINGS(['y']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_CHANGE_STRETCH,
                        None,
                    ),
                ),
            'best_fit_mode':
                MAP(
                    INFO(group_pagefit, 'Best fit mode'),
                    KEYBINDINGS(['b']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_CHANGE_ZOOM_MODE,
                        {'value': ZoomModes.BEST},
                    ),
                ),
            'fit_width_mode':
                MAP(
                    INFO(group_pagefit, 'Fit width mode'),
                    KEYBINDINGS(['w']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_CHANGE_ZOOM_MODE,
                        {'value': ZoomModes.WIDTH},
                    ),
                ),
            'fit_height_mode':
                MAP(
                    INFO(group_pagefit, 'Fit height mode'),
                    KEYBINDINGS(['h']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_CHANGE_ZOOM_MODE,
                        {'value': ZoomModes.HEIGHT},
                    ),
                ),
            'fit_size_mode':
                MAP(
                    INFO(group_pagefit, 'Fit size mode'),
                    KEYBINDINGS(['s']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_CHANGE_ZOOM_MODE,
                        {'value': ZoomModes.SIZE},
                    ),
                ),
            'fit_manual_mode':
                MAP(
                    INFO(group_pagefit, 'Manual zoom mode'),
                    KEYBINDINGS(['a']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_CHANGE_ZOOM_MODE,
                        {'value': ZoomModes.MANUAL},
                    ),
                ),

            # General UI
            'exit_fullscreen':
                MAP(
                    INFO(group_ui, 'Exit from fullscreen'),
                    KEYBINDINGS(['Escape']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_ESCAPE,
                        None,
                    ),
                ),
            'fullscreen':
                MAP(
                    INFO(group_ui, 'Fullscreen'),
                    KEYBINDINGS(['f', 'F11']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_CHANGE_FULLSCREEN,
                        None,
                    ),
                ),
            'minimize':
                MAP(
                    INFO(group_ui, 'Minimize'),
                    KEYBINDINGS(['n']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_MINIMIZE,
                        None,
                    ),
                ),

            # Info
            'about':
                MAP(
                    INFO(group_info, 'About'),
                    KEYBINDINGS(['F1']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_OPEN_DIALOG_ABOUT,
                        None,
                    ),
                ),

            # File operations
            'close':
                MAP(
                    INFO(group_file, 'Close'),
                    KEYBINDINGS(['<Control>W']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_FILE_CLOSE,
                        None,
                    ),
                ),
            'delete':
                MAP(
                    INFO(group_file, 'Delete'),
                    KEYBINDINGS(['Delete']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_FILE_TRASH,
                        None,
                    ),
                ),
            'extract_page':
                MAP(
                    INFO(group_file, 'Extract Page'),
                    KEYBINDINGS(['<Control><Shift>s']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_EXTRACT_PAGE,
                        None,
                    ),
                ),
            'move_file':
                MAP(
                    INFO(group_file, 'Move to subdirectory'),
                    KEYBINDINGS(['Insert', 'grave']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_FILE_MOVE,
                        None,
                    ),
                ),
            'open':
                MAP(
                    INFO(group_file, 'Open'),
                    KEYBINDINGS(['<Control>O']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_OPEN_DIALOG_FILECHOOSER,
                        None,
                    ),
                ),
            'preferences':
                MAP(
                    INFO(group_file, 'Preferences'),
                    KEYBINDINGS(['F12']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_OPEN_DIALOG_PREFERENCES,
                        None,
                    ),
                ),
            'properties':
                MAP(
                    INFO(group_file, 'Properties'),
                    KEYBINDINGS(['<Alt>Return']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_OPEN_DIALOG_PROPERTIES,
                        None,
                    ),
                ),
            'quit':
                MAP(
                    INFO(group_file, 'Quit'),
                    KEYBINDINGS(['<Control>Q']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_EXIT,
                        None,
                    ),
                ),
            'refresh_archive':
                MAP(
                    INFO(group_file, 'Refresh'),
                    KEYBINDINGS(['<control><shift>R']),
                    KEY_EVENT(
                        events.run_events,
                        EventType.KB_FILE_REFRESH,
                        None,
                    ),
                ),
        }

    @property
    def bindings(self):
        return self.__bindings
