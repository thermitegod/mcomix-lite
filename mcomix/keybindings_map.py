# -*- coding: utf-8 -*-

#: Bindings defined in this dictionary will appear in the configuration dialog.
#: If 'group' is None, the binding cannot be modified from the preferences dialog.

from dataclasses import dataclass
from typing import Callable

from mcomix.constants import Constants
from mcomix.preferences import config


class KeyBindingsMap:
    def __init__(self, window):
        super().__init__()

        group_nav = 'Navigation'
        group_scroll = 'Scrolling'
        group_zoom = 'Zoom'
        group_trans = 'Transformation'
        group_rotate = 'Autorotate'
        group_view = 'View mode'
        group_pagefit = 'Page fit mode'
        group_ui = 'User interface'
        group_info = 'Info'
        group_file = 'File'
        group_scale = 'Image Scaling'

        @dataclass(frozen=True)
        class INFO:
            __slots__ = ['group', 'title']
            group: str
            title: str

        @dataclass(frozen=True)
        class KEYBINDINGS:
            __slots__ = ['keybindings']
            keybindings: list

        @dataclass(frozen=True)
        class KEY_EVENT:
            __slots__ = ['callback', 'callback_kwargs']
            callback: Callable
            callback_kwargs: dict

        @dataclass(frozen=True)
        class MAP:
            __slots__ = ['info', 'keybindings', 'key_event']
            info: INFO
            keybindings: KEYBINDINGS
            key_event: KEY_EVENT

        self.BINDINGS = {
            # Navigation
            'previous_page':
                MAP(
                    INFO(group_nav, 'Previous page'),
                    KEYBINDINGS(['Page_Up', 'KP_Page_Up', 'BackSpace']),
                    KEY_EVENT(
                        window.flip_page,
                        {'number_of_pages': -1},
                    ),
                ),
            'next_page':
                MAP(
                    INFO(group_nav, 'Next page'),
                    KEYBINDINGS(['Page_Down', 'KP_Page_Down']),
                    KEY_EVENT(
                        window.flip_page,
                        {'number_of_pages': +1},
                    ),
                ),
            'previous_page_singlestep':
                MAP(
                    INFO(group_nav, 'Previous page (always one page)'),
                    KEYBINDINGS(['<Primary>Up', '<Primary>Page_Up', '<Primary>KP_Page_Up']),
                    KEY_EVENT(
                        window.flip_page,
                        {'number_of_pages': -1, 'single_step': True},
                    ),
                ),
            'next_page_singlestep':
                MAP(
                    INFO(group_nav, 'Next page (always one page)'),
                    KEYBINDINGS(['<Primary>Down', '<Primary>Page_Down', '<Primary>KP_Page_Down']),
                    KEY_EVENT(
                        window.flip_page,
                        {'number_of_pages': +1, 'single_step': True},
                    ),
                ),
            'previous_page_ff':
                MAP(
                    INFO(group_nav, 'Rewind by X pages'),
                    KEYBINDINGS(['<Shift>Page_Up', '<Shift>KP_Page_Up', '<Shift>BackSpace', '<Shift><Mod1>Left']),
                    KEY_EVENT(
                        window.flip_page,
                        {'number_of_pages': -config['PAGE_FF_STEP']},
                    ),
                ),
            'next_page_ff':
                MAP(
                    INFO(group_nav, 'Forward by X pages'),
                    KEYBINDINGS(['<Shift>Page_Down', '<Shift>KP_Page_Down', '<Shift><Mod1>Right']),
                    KEY_EVENT(
                        window.flip_page,
                        {'number_of_pages': +config['PAGE_FF_STEP']},
                    ),
                ),
            'first_page':
                MAP(
                    INFO(group_nav, 'First page'),
                    KEYBINDINGS(['Home', 'KP_Home']),
                    KEY_EVENT(
                        window.first_page,
                        None,
                    ),
                ),
            'last_page':
                MAP(
                    INFO(group_nav, 'Last page'),
                    KEYBINDINGS(['End', 'KP_End']),
                    KEY_EVENT(
                        window.last_page,
                        None,
                    ),
                ),
            'go_to':
                MAP(
                    INFO(group_nav, 'Go to page'),
                    KEYBINDINGS(['G']),
                    KEY_EVENT(
                        window.page_select,
                        None,
                    ),
                ),
            'next_archive':
                MAP(
                    INFO(group_nav, 'Next archive'),
                    KEYBINDINGS(['<Primary>Right']),
                    KEY_EVENT(
                        window.filehandler.open_archive_direction,
                        {'forward': True},
                    ),
                ),
            'previous_archive':
                MAP(
                    INFO(group_nav, 'Previous archive'),
                    KEYBINDINGS(['<Primary>Left']),
                    KEY_EVENT(
                        window.filehandler.open_archive_direction,
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
                        window.event_handler.scroll_with_flipping,
                        {'x': 0, 'y': config['PIXELS_TO_SCROLL_PER_KEY_EVENT']},
                    ),
                ),
            'scroll_left':
                MAP(
                    INFO(group_scroll, 'Scroll left'),
                    KEYBINDINGS(['Left', 'KP_Left']),
                    KEY_EVENT(
                        window.event_handler.scroll_with_flipping,
                        {'x': -config['PIXELS_TO_SCROLL_PER_KEY_EVENT'], 'y': 0},
                    ),
                ),
            'scroll_right':
                MAP(
                    INFO(group_scroll, 'Scroll right'),
                    KEYBINDINGS(['Right', 'KP_Right']),
                    KEY_EVENT(
                        window.event_handler.scroll_with_flipping,
                        {'x': config['PIXELS_TO_SCROLL_PER_KEY_EVENT'], 'y': 0},
                    ),
                ),
            'scroll_up':
                MAP(
                    INFO(group_scroll, 'Scroll up'),
                    KEYBINDINGS(['Up', 'KP_Up']),
                    KEY_EVENT(
                        window.event_handler.scroll_with_flipping,
                        {'x': 0, 'y': -config['PIXELS_TO_SCROLL_PER_KEY_EVENT']},
                    ),
                ),

            # View
            'zoom_original':
                MAP(
                    INFO(group_zoom, 'Normal size'),
                    KEYBINDINGS(['<Control>0', 'KP_0']),
                    KEY_EVENT(
                        window.manual_zoom_original,
                        None,
                    ),
                ),
            'zoom_in':
                MAP(
                    INFO(group_zoom, 'Zoom in'),
                    KEYBINDINGS(['plus', 'KP_Add', 'equal']),
                    KEY_EVENT(
                        window.manual_zoom_in,
                        None,
                    ),
                ),
            'zoom_out':
                MAP(
                    INFO(group_zoom, 'Zoom out'),
                    KEYBINDINGS(['minus', 'KP_Subtract']),
                    KEY_EVENT(
                        window.manual_zoom_out,
                        None,
                    ),
                ),

            # Zoom out is already defined as GTK menu hotkey
            'keep_transformation':
                MAP(
                    INFO(group_trans, 'Keep transformation'),
                    KEYBINDINGS(['k']),
                    KEY_EVENT(
                        window.change_keep_transformation,
                        None,
                    ),
                ),
            'rotate_90':
                MAP(
                    INFO(group_trans, 'Rotate 90°'),
                    KEYBINDINGS(['r']),
                    KEY_EVENT(
                        window.rotate_x,
                        {'rotation': 90},
                    ),
                ),
            'rotate_180':
                MAP(
                    INFO(group_trans, 'Rotate 180°'),
                    KEYBINDINGS([]),
                    KEY_EVENT(
                        window.rotate_x,
                        {'rotation': 180},
                    ),
                ),
            'rotate_270':
                MAP(
                    INFO(group_trans, 'Rotate 270°'),
                    KEYBINDINGS(['<Shift>r']),
                    KEY_EVENT(
                        window.rotate_x,
                        {'rotation': 270},
                    ),
                ),

            # Autorotate
            'no_autorotation':
                MAP(
                    INFO(group_rotate, 'Never autorotate'),
                    KEYBINDINGS([]),
                    KEY_EVENT(
                        window.change_autorotation,
                        {'value': Constants.AUTOROTATE['NEVER']},
                    ),
                ),
            'rotate_90_width':
                MAP(
                    INFO(group_rotate, 'Rotate width 90°'),
                    KEYBINDINGS([]),
                    KEY_EVENT(
                        window.change_autorotation,
                        {'value': Constants.AUTOROTATE['WIDTH_90']},
                    ),
                ),
            'rotate_270_width':
                MAP(
                    INFO(group_rotate, 'Rotate width 270°'),
                    KEYBINDINGS([]),
                    KEY_EVENT(
                        window.change_autorotation,
                        {'value': Constants.AUTOROTATE['WIDTH_270']},
                    ),
                ),
            'rotate_90_height':
                MAP(
                    INFO(group_rotate, 'Rotate height 90°'),
                    KEYBINDINGS([]),
                    KEY_EVENT(
                        window.change_autorotation,
                        {'value': Constants.AUTOROTATE['HEIGHT_90']},
                    ),
                ),
            'rotate_270_height':
                MAP(
                    INFO(group_rotate, 'Rotate height 270°'),
                    KEYBINDINGS([]),
                    KEY_EVENT(
                        window.change_autorotation,
                        {'value': Constants.AUTOROTATE['HEIGHT_270']},
                    ),
                ),

            # View mode
            'double_page':
                MAP(
                    INFO(group_view, 'Double page mode'),
                    KEYBINDINGS(['d']),
                    KEY_EVENT(
                        window.change_double_page,
                        None,
                    ),
                ),
            'manga_mode':
                MAP(
                    INFO(group_view, 'Manga mode'),
                    KEYBINDINGS(['m']),
                    KEY_EVENT(
                        window.change_manga_mode,
                        None,
                    ),
                ),

            # Fit mode
            'stretch':
                MAP(
                    INFO(group_pagefit, 'Stretch small images'),
                    KEYBINDINGS(['y']),
                    KEY_EVENT(
                        window.change_stretch,
                        None,
                    ),
                ),
            'best_fit_mode':
                MAP(
                    INFO(group_pagefit, 'Best fit mode'),
                    KEYBINDINGS(['b']),
                    KEY_EVENT(
                        window.change_fit_mode_best,
                        None,
                    ),
                ),
            'fit_width_mode':
                MAP(
                    INFO(group_pagefit, 'Fit width mode'),
                    KEYBINDINGS(['w']),
                    KEY_EVENT(
                        window.change_fit_mode_width,
                        None,
                    ),
                ),
            'fit_height_mode':
                MAP(
                    INFO(group_pagefit, 'Fit height mode'),
                    KEYBINDINGS(['h']),
                    KEY_EVENT(
                        window.change_fit_mode_height,
                        None,
                    ),
                ),
            'fit_size_mode':
                MAP(
                    INFO(group_pagefit, 'Fit size mode'),
                    KEYBINDINGS(['s']),
                    KEY_EVENT(
                        window.change_fit_mode_size,
                        None,
                    ),
                ),
            'fit_manual_mode':
                MAP(
                    INFO(group_pagefit, 'Manual zoom mode'),
                    KEYBINDINGS(['a']),
                    KEY_EVENT(
                        window.change_fit_mode_manual,
                        None,
                    ),
                ),

            # General UI
            'exit_fullscreen':
                MAP(
                    INFO(group_ui, 'Exit from fullscreen'),
                    KEYBINDINGS(['Escape']),
                    KEY_EVENT(
                        window.event_handler.escape_event,
                        None,
                    ),
                ),
            'fullscreen':
                MAP(
                    INFO(group_ui, 'Fullscreen'),
                    KEYBINDINGS(['f', 'F11']),
                    KEY_EVENT(
                        window.change_fullscreen,
                        None,
                    ),
                ),
            'minimize':
                MAP(
                    INFO(group_ui, 'Minimize'),
                    KEYBINDINGS(['n']),
                    KEY_EVENT(
                        window.minimize,
                        None,
                    ),
                ),

            # Info
            'about':
                MAP(
                    INFO(group_info, 'About'),
                    KEYBINDINGS(['F1']),
                    KEY_EVENT(
                        window.open_dialog_about,
                        None,
                    ),
                ),

            # File operations
            'close':
                MAP(
                    INFO(group_file, 'Close'),
                    KEYBINDINGS(['<Control>W']),
                    KEY_EVENT(
                        window.filehandler.close_file,
                        None,
                    ),
                ),
            'delete':
                MAP(
                    INFO(group_file, 'Delete'),
                    KEYBINDINGS(['Delete']),
                    KEY_EVENT(
                        window.trash_file,
                        None,
                    ),
                ),
            'enhance_image':
                MAP(
                    INFO(group_file, 'Enhance image'),
                    KEYBINDINGS(['e']),
                    KEY_EVENT(
                        window.open_dialog_enhance,
                        None,
                    ),
                ),
            'extract_page':
                MAP(
                    INFO(group_file, 'Extract Page'),
                    KEYBINDINGS(['<Control><Shift>s']),
                    KEY_EVENT(
                        window.extract_page,
                        None,
                    ),
                ),
            'move_file':
                MAP(
                    INFO(group_file, 'Move to subdirectory'),
                    KEYBINDINGS(['Insert', 'grave']),
                    KEY_EVENT(
                        window.move_file,
                        None,
                    ),
                ),
            'open':
                MAP(
                    INFO(group_file, 'Open'),
                    KEYBINDINGS(['<Control>O']),
                    KEY_EVENT(
                        window.open_dialog_file_chooser,
                        None,
                    ),
                ),
            'preferences':
                MAP(
                    INFO(group_file, 'Preferences'),
                    KEYBINDINGS(['F12']),
                    KEY_EVENT(
                        window.open_dialog_preference,
                        None,
                    ),
                ),
            'properties':
                MAP(
                    INFO(group_file, 'Properties'),
                    KEYBINDINGS(['<Alt>Return']),
                    KEY_EVENT(
                        window.open_dialog_properties,
                        None,
                    ),
                ),
            'quit':
                MAP(
                    INFO(group_file, 'Quit'),
                    KEYBINDINGS(['<Control>Q']),
                    KEY_EVENT(
                        window.terminate_program,
                        None,
                    ),
                ),
            'refresh_archive':
                MAP(
                    INFO(group_file, 'Refresh'),
                    KEYBINDINGS(['<control><shift>R']),
                    KEY_EVENT(
                        window.filehandler.refresh_file,
                        None,
                    ),
                ),

            # Image Scaling
            'toggle_scaling_pil':
                MAP(
                    INFO(group_scale, 'Toggle GDK/PIL Image scaling'),
                    KEYBINDINGS(['c']),
                    KEY_EVENT(
                        window.toggle_image_scaling,
                        None,
                    ),
                ),
            'scaling_inc':
                MAP(
                    INFO(group_scale, 'Cycle GDK/PIL Image scaling forward'),
                    KEYBINDINGS(['z']),
                    KEY_EVENT(
                        window.change_image_scaling,
                        {'step': +1},
                    ),
                ),
            'scaling_dec':
                MAP(
                    INFO(group_scale, 'Cycle GDK/PIL Image scaling backwards'),
                    KEYBINDINGS(['x']),
                    KEY_EVENT(
                        window.change_image_scaling,
                        {'step': -1},
                    ),
                ),
        }
