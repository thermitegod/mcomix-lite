# -*- coding: utf-8 -*-

#: Bindings defined in this dictionary will appear in the configuration dialog.
#: If 'group' is None, the binding cannot be modified from the preferences dialog.

from collections import namedtuple


class _KeyBindingsMap:
    def __init__(self):
        super().__init__()

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

        MAP = namedtuple('MAP', ['info', 'keybindings'])
        INFO = namedtuple('INFO', ['group', 'title'])

        self.BINDINGS = {
            # Navigation
            'previous_page':
                MAP(
                    INFO(nav, 'Previous page'),
                    ['Page_Up', 'KP_Page_Up', 'BackSpace']
                ),
            'next_page':
                MAP(
                    INFO(nav, 'Next page'),
                    ['Page_Down', 'KP_Page_Down']
                ),
            'previous_page_singlestep':
                MAP(
                    INFO(nav, 'Previous page (always one page)'),
                    ['<Primary>Up', '<Primary>Page_Up', '<Primary>KP_Page_Up']
                ),
            'next_page_singlestep':
                MAP(
                    INFO(nav, 'Next page (always one page)'),
                    ['<Primary>Down', '<Primary>Page_Down', '<Primary>KP_Page_Down']
                ),
            'previous_page_ff':
                MAP(
                    INFO(nav, 'Rewind by X pages'),
                    ['<Shift>Page_Up', '<Shift>KP_Page_Up', '<Shift>BackSpace', '<Shift><Mod1>Left']
                ),
            'next_page_ff':
                MAP(
                    INFO(nav, 'Forward by X pages'),
                    ['<Shift>Page_Down', '<Shift>KP_Page_Down', '<Shift><Mod1>Right']
                ),
            'first_page':
                MAP(
                    INFO(nav, 'First page'),
                    ['Home', 'KP_Home']
                ),
            'last_page':
                MAP(
                    INFO(nav, 'Last page'),
                    ['End', 'KP_End']
                ),
            'go_to':
                MAP(
                    INFO(nav, 'Go to page'),
                    ['G']
                ),
            'next_archive':
                MAP(
                    INFO(nav, 'Next archive'),
                    ['<Primary>Right']
                ),
            'previous_archive':
                MAP(
                    INFO(nav, 'Previous archive'),
                    ['<Primary>Left']
                ),

            # Scrolling
            # Arrow keys scroll the image
            'scroll_down':
                MAP(
                    INFO(scroll, 'Scroll down'),
                    ['Down', 'KP_Down']
                ),
            'scroll_left':
                MAP(
                    INFO(scroll, 'Scroll left'),
                    ['Left', 'KP_Left']
                ),
            'scroll_right':
                MAP(
                    INFO(scroll, 'Scroll right'),
                    ['Right', 'KP_Right']
                ),
            'scroll_up':
                MAP(
                    INFO(scroll, 'Scroll up'),
                    ['Up', 'KP_Up']
                ),

            # View
            'zoom_original':
                MAP(
                    INFO(zoom, 'Normal size'),
                    ['<Control>0', 'KP_0']
                ),
            'zoom_in':
                MAP(
                    INFO(zoom, 'Zoom in'),
                    ['plus', 'KP_Add', 'equal']
                ),
            'zoom_out':
                MAP(
                    INFO(zoom, 'Zoom out'),
                    ['minus', 'KP_Subtract']
                ),

            # Zoom out is already defined as GTK menu hotkey
            'keep_transformation':
                MAP(
                    INFO(trans, 'Keep transformation'),
                    ['k']
                ),
            'rotate_90':
                MAP(
                    INFO(trans, 'Rotate 90°'),
                    ['r']
                ),
            'rotate_180':
                MAP(
                    INFO(trans, 'Rotate 180°'),
                    []
                ),
            'rotate_270':
                MAP(
                    INFO(trans, 'Rotate 270°'),
                    ['<Shift>r']
                ),
            'flip_horiz':
                MAP(
                    INFO(trans, 'Flip horizontally'),
                    []
                ),
            'flip_vert':
                MAP(
                    INFO(trans, 'Flip vertically'),
                    []
                ),
            'no_autorotation':
                MAP(
                    INFO(trans, 'Never autorotate'),
                    []
                ),

            # Autorotate
            'rotate_90_width':
                MAP(
                    INFO(rotate, 'Rotate width 90°'),
                    []
                ),
            'rotate_270_width':
                MAP(
                    INFO(rotate, 'Rotate width 270°'),
                    []
                ),
            'rotate_90_height':
                MAP(
                    INFO(rotate, 'Rotate height 90°'),
                    []
                ),
            'rotate_270_height':
                MAP(
                    INFO(rotate, 'Rotate height 270°'),
                    []
                ),

            # View mode
            'double_page':
                MAP(
                    INFO(view, 'Double page mode'),
                    ['d']
                ),
            'manga_mode':
                MAP(
                    INFO(view, 'Manga mode'),
                    ['m']
                ),
            'lens':
                MAP(
                    INFO(view, 'Magnifying lens'),
                    ['l']
                ),
            'stretch':
                MAP(
                    INFO(view, 'Stretch small images'),
                    ['y']
                ),

            # Fit mode
            'best_fit_mode':
                MAP(
                    INFO(pagefit, 'Best fit mode'),
                    ['b']
                ),
            'fit_width_mode':
                MAP(
                    INFO(pagefit, 'Fit width mode'),
                    ['w']
                ),
            'fit_height_mode':
                MAP(
                    INFO(pagefit, 'Fit height mode'),
                    ['h']
                ),
            'fit_size_mode':
                MAP(
                    INFO(pagefit, 'Fit size mode'),
                    ['s']
                ),
            'fit_manual_mode':
                MAP(
                    INFO(pagefit, 'Manual zoom mode'),
                    ['a']
                ),

            # General UI
            'exit_fullscreen':
                MAP(
                    INFO(ui, 'Exit from fullscreen'),
                    ['Escape']
                ),
            'fullscreen':
                MAP(
                    INFO(ui, 'Fullscreen'),
                    ['f', 'F11']
                ),
            'minimize':
                MAP(
                    INFO(ui, 'Minimize'),
                    ['n']
                ),
            'hide_all':
                MAP(
                    INFO(ui, 'Show/hide all'),
                    ['i']
                ),
            'menubar':
                MAP(
                    INFO(ui, 'Show/hide menubar'),
                    ['<Control>M']
                ),
            'scrollbar':
                MAP(
                    INFO(ui, 'Show/hide scrollbars'),
                    []
                ),
            'statusbar':
                MAP(
                    INFO(ui, 'Show/hide statusbar'),
                    []
                ),
            'thumbnails':
                MAP(
                    INFO(ui, 'Thumbnails'),
                    ['F9']
                ),

            # Info
            'about':
                MAP(
                    INFO(info, 'About'),
                    ['F1']
                ),

            # File operations
            'close':
                MAP(
                    INFO(file, 'Close'),
                    ['<Control>W']
                ),
            'delete':
                MAP(
                    INFO(file, 'Delete'),
                    ['Delete']
                ),
            'enhance_image':
                MAP(
                    INFO(file, 'Enhance image'),
                    ['e']
                ),
            'extract_page':
                MAP(
                    INFO(file, 'Extract Page'),
                    ['<Control><Shift>s']
                ),
            'move_file':
                MAP(
                    INFO(file, 'Move to subdirectory'),
                    ['Insert', 'grave']
                ),
            'open':
                MAP(
                    INFO(file, 'Open'),
                    ['<Control>O']
                ),
            'preferences':
                MAP(
                    INFO(file, 'Preferences'),
                    ['F12']
                ),
            'properties':
                MAP(
                    INFO(file, 'Properties'),
                    ['<Alt>Return']
                ),
            'quit':
                MAP(
                    INFO(file, 'Quit'),
                    ['<Control>Q']
                ),
            'refresh_archive':
                MAP(
                    INFO(file, 'Refresh'),
                    ['<control><shift>R']
                ),
        }


KeyBindingsMap = _KeyBindingsMap()
