# -*- coding: utf-8 -*-

#: Bindings defined in this dictionary will appear in the configuration dialog.
#: If 'group' is None, the binding cannot be modified from the preferences dialog.

from collections import namedtuple

from mcomix.preferences import config


class KeyBindingsMap:
    def __init__(self, window):
        super().__init__()

        self.__window = window

        nav = 'Navigation'
        scroll = 'Scrolling'
        zoom = 'Zoom'
        trans = 'Transformation'
        rotate = 'Autorotate'
        view = 'View mode'
        pagefit = 'Page fit mode'
        ui = 'User interface'
        info = 'Info'
        file = 'File'

        MAP = namedtuple('MAP', ['info', 'keybindings', 'key_event'])
        INFO = namedtuple('INFO', ['group', 'title'])
        KEY_EVENT = namedtuple('KEY_EVENT', ['callback', 'callback_kwargs'])

        self.BINDINGS = {
            # Navigation
            'previous_page':
                MAP(
                    INFO(nav, 'Previous page'),
                    ['Page_Up', 'KP_Page_Up', 'BackSpace'],
                    KEY_EVENT(
                        self.__window.flip_page,
                        {'number_of_pages': -1},
                    ),
                ),
            'next_page':
                MAP(
                    INFO(nav, 'Next page'),
                    ['Page_Down', 'KP_Page_Down'],
                    KEY_EVENT(
                        self.__window.flip_page,
                        {'number_of_pages': +1},
                    ),
                ),
            'previous_page_singlestep':
                MAP(
                    INFO(nav, 'Previous page (always one page)'),
                    ['<Primary>Up', '<Primary>Page_Up', '<Primary>KP_Page_Up'],
                    KEY_EVENT(
                        self.__window.flip_page,
                        {'number_of_pages': -1, 'single_step': True},
                    ),
                ),
            'next_page_singlestep':
                MAP(
                    INFO(nav, 'Next page (always one page)'),
                    ['<Primary>Down', '<Primary>Page_Down', '<Primary>KP_Page_Down'],
                    KEY_EVENT(
                        self.__window.flip_page,
                        {'number_of_pages': +1, 'single_step': True},
                    ),
                ),
            'previous_page_ff':
                MAP(
                    INFO(nav, 'Rewind by X pages'),
                    ['<Shift>Page_Up', '<Shift>KP_Page_Up', '<Shift>BackSpace', '<Shift><Mod1>Left'],
                    KEY_EVENT(
                        self.__window.flip_page,
                        {'number_of_pages': -config['PAGE_FF_STEP']},
                    ),
                ),
            'next_page_ff':
                MAP(
                    INFO(nav, 'Forward by X pages'),
                    ['<Shift>Page_Down', '<Shift>KP_Page_Down', '<Shift><Mod1>Right'],
                    KEY_EVENT(
                        self.__window.flip_page,
                        {'number_of_pages': +config['PAGE_FF_STEP']},
                    ),
                ),
            'first_page':
                MAP(
                    INFO(nav, 'First page'),
                    ['Home', 'KP_Home'],
                    KEY_EVENT(
                        self.__window.first_page,
                        None,
                    ),
                ),
            'last_page':
                MAP(
                    INFO(nav, 'Last page'),
                    ['End', 'KP_End'],
                    KEY_EVENT(
                        self.__window.last_page,
                        None,
                    ),
                ),
            'go_to':
                MAP(
                    INFO(nav, 'Go to page'),
                    ['G'],
                    KEY_EVENT(
                        self.__window.page_select,
                        None,
                    ),
                ),
            'next_archive':
                MAP(
                    INFO(nav, 'Next archive'),
                    ['<Primary>Right'],
                    KEY_EVENT(
                        self.__window.filehandler.open_archive_direction,
                        {'forward': True},
                    ),
                ),
            'previous_archive':
                MAP(
                    INFO(nav, 'Previous archive'),
                    ['<Primary>Left'],
                    KEY_EVENT(
                        self.__window.filehandler.open_archive_direction,
                        {'forward': False},
                    ),
                ),

            # Scrolling
            # Arrow keys scroll the image
            'scroll_down':
                MAP(
                    INFO(scroll, 'Scroll down'),
                    ['Down', 'KP_Down'],
                    KEY_EVENT(
                        self.__window.event_handler.scroll_with_flipping,
                        {'x': 0, 'y': config['PIXELS_TO_SCROLL_PER_KEY_EVENT']},
                    ),
                ),
            'scroll_left':
                MAP(
                    INFO(scroll, 'Scroll left'),
                    ['Left', 'KP_Left'],
                    KEY_EVENT(
                        self.__window.event_handler.scroll_with_flipping,
                        {'x': -config['PIXELS_TO_SCROLL_PER_KEY_EVENT'], 'y': 0},
                    ),
                ),
            'scroll_right':
                MAP(
                    INFO(scroll, 'Scroll right'),
                    ['Right', 'KP_Right'],
                    KEY_EVENT(
                        self.__window.event_handler.scroll_with_flipping,
                        {'x': config['PIXELS_TO_SCROLL_PER_KEY_EVENT'], 'y': 0},
                    ),
                ),
            'scroll_up':
                MAP(
                    INFO(scroll, 'Scroll up'),
                    ['Up', 'KP_Up'],
                    KEY_EVENT(
                        self.__window.event_handler.scroll_with_flipping,
                        {'x': 0, 'y': -config['PIXELS_TO_SCROLL_PER_KEY_EVENT']},
                    ),
                ),

            # View
            'zoom_original':
                MAP(
                    INFO(zoom, 'Normal size'),
                    ['<Control>0', 'KP_0'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('zoom_original').activate,
                        None,
                    ),
                ),
            'zoom_in':
                MAP(
                    INFO(zoom, 'Zoom in'),
                    ['plus', 'KP_Add', 'equal'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('zoom_in').activate,
                        None,
                    ),
                ),
            'zoom_out':
                MAP(
                    INFO(zoom, 'Zoom out'),
                    ['minus', 'KP_Subtract'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('zoom_out').activate,
                        None,
                    ),
                ),

            # Zoom out is already defined as GTK menu hotkey
            'keep_transformation':
                MAP(
                    INFO(trans, 'Keep transformation'),
                    ['k'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('keep_transformation').activate,
                        None,
                    ),
                ),
            'rotate_90':
                MAP(
                    INFO(trans, 'Rotate 90°'),
                    ['r'],
                    KEY_EVENT(
                        self.__window.rotate_x,
                        {'rotation': 90},
                    ),
                ),
            'rotate_180':
                MAP(
                    INFO(trans, 'Rotate 180°'),
                    [],
                    KEY_EVENT(
                        self.__window.rotate_x,
                        {'rotation': 180},
                    ),
                ),
            'rotate_270':
                MAP(
                    INFO(trans, 'Rotate 270°'),
                    ['<Shift>r'],
                    KEY_EVENT(
                        self.__window.rotate_x,
                        {'rotation': 270},
                    ),
                ),
            'flip_horiz':
                MAP(
                    INFO(trans, 'Flip horizontally'),
                    [],
                    KEY_EVENT(
                        self.__window.flip_horizontally,
                        None,
                    ),
                ),
            'flip_vert':
                MAP(
                    INFO(trans, 'Flip vertically'),
                    [],
                    KEY_EVENT(
                        self.__window.flip_vertically,
                        None,
                    ),
                ),
            'no_autorotation':
                MAP(
                    INFO(trans, 'Never autorotate'),
                    [],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('no_autorotation').activate,
                        None,
                    ),
                ),

            # Autorotate
            'rotate_90_width':
                MAP(
                    INFO(rotate, 'Rotate width 90°'),
                    [],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('rotate_90_width').activate,
                        None,
                    ),
                ),
            'rotate_270_width':
                MAP(
                    INFO(rotate, 'Rotate width 270°'),
                    [],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('rotate_270_width').activate,
                        None,
                    ),
                ),
            'rotate_90_height':
                MAP(
                    INFO(rotate, 'Rotate height 90°'),
                    [],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('rotate_90_height').activate,
                        None,
                    ),
                ),
            'rotate_270_height':
                MAP(
                    INFO(rotate, 'Rotate height 270°'),
                    [],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('rotate_270_height').activate,
                        None,
                    ),
                ),

            # View mode
            'double_page':
                MAP(
                    INFO(view, 'Double page mode'),
                    ['d'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('double_page').activate,
                        None,
                    ),
                ),
            'manga_mode':
                MAP(
                    INFO(view, 'Manga mode'),
                    ['m'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('manga_mode').activate,
                        None,
                    ),
                ),
            'lens':
                MAP(
                    INFO(view, 'Magnifying lens'),
                    ['l'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('lens').activate,
                        None,
                    ),
                ),
            'stretch':
                MAP(
                    INFO(view, 'Stretch small images'),
                    ['y'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('stretch').activate,
                        None,
                    ),
                ),

            # Fit mode
            'best_fit_mode':
                MAP(
                    INFO(pagefit, 'Best fit mode'),
                    ['b'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('best_fit_mode').activate,
                        None,
                    ),
                ),
            'fit_width_mode':
                MAP(
                    INFO(pagefit, 'Fit width mode'),
                    ['w'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('fit_width_mode').activate,
                        None,
                    ),
                ),
            'fit_height_mode':
                MAP(
                    INFO(pagefit, 'Fit height mode'),
                    ['h'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('fit_height_mode').activate,
                        None,
                    ),
                ),
            'fit_size_mode':
                MAP(
                    INFO(pagefit, 'Fit size mode'),
                    ['s'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('fit_size_mode').activate,
                        None,
                    ),
                ),
            'fit_manual_mode':
                MAP(
                    INFO(pagefit, 'Manual zoom mode'),
                    ['a'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('fit_manual_mode').activate,
                        None,
                    ),
                ),

            # General UI
            'exit_fullscreen':
                MAP(
                    INFO(ui, 'Exit from fullscreen'),
                    ['Escape'],
                    KEY_EVENT(
                        self.__window.event_handler.escape_event,
                        None,
                    ),
                ),
            'fullscreen':
                MAP(
                    INFO(ui, 'Fullscreen'),
                    ['f', 'F11'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('fullscreen').activate,
                        None,
                    ),
                ),
            'minimize':
                MAP(
                    INFO(ui, 'Minimize'),
                    ['n'],
                    KEY_EVENT(
                        self.__window.minimize,
                        None,
                    ),
                ),
            'hide_all':
                MAP(
                    INFO(ui, 'Show/hide all'),
                    ['i'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('hide_all').activate,
                        None,
                    ),
                ),
            'menubar':
                MAP(
                    INFO(ui, 'Show/hide menubar'),
                    ['<Control>M'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('menubar').activate,
                        None,
                    ),
                ),
            'scrollbar':
                MAP(
                    INFO(ui, 'Show/hide scrollbars'),
                    [],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('scrollbar').activate,
                        None,
                    ),
                ),
            'statusbar':
                MAP(
                    INFO(ui, 'Show/hide statusbar'),
                    [],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('statusbar').activate,
                        None,
                    ),
                ),
            'thumbnails':
                MAP(
                    INFO(ui, 'Thumbnails'),
                    ['F9'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('thumbnails').activate,
                        None,
                    ),
                ),

            # Info
            'about':
                MAP(
                    INFO(info, 'About'),
                    ['F1'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('about').activate,
                        None,
                    ),
                ),

            # File operations
            'close':
                MAP(
                    INFO(file, 'Close'),
                    ['<Control>W'],
                    KEY_EVENT(
                        self.__window.filehandler.close_file,
                        None,
                    ),
                ),
            'delete':
                MAP(
                    INFO(file, 'Delete'),
                    ['Delete'],
                    KEY_EVENT(
                        self.__window.move_file,
                        {'move_else_delete': False},
                    ),
                ),
            'enhance_image':
                MAP(
                    INFO(file, 'Enhance image'),
                    ['e'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('enhance_image').activate,
                        None,
                    ),
                ),
            'extract_page':
                MAP(
                    INFO(file, 'Extract Page'),
                    ['<Control><Shift>s'],
                    KEY_EVENT(
                        self.__window.extract_page,
                        None,
                    ),
                ),
            'move_file':
                MAP(
                    INFO(file, 'Move to subdirectory'),
                    ['Insert', 'grave'],
                    KEY_EVENT(
                        self.__window.move_file,
                        {'move_else_delete': True},
                    ),
                ),
            'open':
                MAP(
                    INFO(file, 'Open'),
                    ['<Control>O'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('open').activate,
                        None,
                    ),
                ),
            'preferences':
                MAP(
                    INFO(file, 'Preferences'),
                    ['F12'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('preferences').activate,
                        None,
                    ),
                ),
            'properties':
                MAP(
                    INFO(file, 'Properties'),
                    ['<Alt>Return'],
                    KEY_EVENT(
                        self.__window.actiongroup.get_action('properties').activate,
                        None,
                    ),
                ),
            'quit':
                MAP(
                    INFO(file, 'Quit'),
                    ['<Control>Q'],
                    KEY_EVENT(
                        self.__window.terminate_program,
                        None,
                    ),
                ),
            'refresh_archive':
                MAP(
                    INFO(file, 'Refresh'),
                    ['<control><shift>R'],
                    KEY_EVENT(
                        self.__window.filehandler.refresh_file,
                        None,
                    ),
                ),
        }
