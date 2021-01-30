# -*- coding: utf-8 -*-

#: Bindings defined in this dictionary will appear in the configuration dialog.
#: If 'group' is None, the binding cannot be modified from the preferences dialog.

from collections import namedtuple


class _KeyBindingsMap:
    def __init__(self):
        super().__init__()

        MAP = namedtuple('MAP', ['info', 'keybindings'])
        INFO = namedtuple('INFO', ['group', 'title'])

        self.BINDINGS = {
            # Navigation
            'previous_page':
                MAP(
                    INFO('Navigation', 'Previous page'),
                    ['Page_Up', 'KP_Page_Up', 'BackSpace']
                ),
            'next_page':
                MAP(
                    INFO('Navigation', 'Next page'),
                    ['Page_Down', 'KP_Page_Down']
                ),
            'previous_page_singlestep':
                MAP(
                    INFO('Navigation', 'Previous page (always one page)'),
                    ['<Primary>Up', '<Primary>Page_Up', '<Primary>KP_Page_Up']
                ),
            'next_page_singlestep':
                MAP(
                    INFO('Navigation', 'Next page (always one page)'),
                    ['<Primary>Down', '<Primary>Page_Down', '<Primary>KP_Page_Down']
                ),
            'previous_page_ff':
                MAP(
                    INFO('Navigation', 'Rewind by X pages'),
                    ['<Shift>Page_Up', '<Shift>KP_Page_Up', '<Shift>BackSpace', '<Shift><Mod1>Left']
                ),
            'next_page_ff':
                MAP(
                    INFO('Navigation', 'Forward by X pages'),
                    ['<Shift>Page_Down', '<Shift>KP_Page_Down', '<Shift><Mod1>Right']
                ),
            'first_page':
                MAP(
                    INFO('Navigation', 'First page'),
                    ['Home', 'KP_Home']
                ),
            'last_page':
                MAP(
                    INFO('Navigation', 'Last page'),
                    ['End', 'KP_End']
                ),
            'go_to':
                MAP(
                    INFO('Navigation', 'Go to page'),
                    ['G']
                ),
            'next_archive':
                MAP(
                    INFO('Navigation', 'Next archive'),
                    ['<Primary>Right']
                ),
            'previous_archive':
                MAP(
                    INFO('Navigation', 'Previous archive'),
                    ['<Primary>Left']
                ),

            # Scrolling
            # Arrow keys scroll the image
            'scroll_down':
                MAP(
                    INFO('Scrolling', 'Scroll down'),
                    ['Down', 'KP_Down']
                ),
            'scroll_left':
                MAP(
                    INFO('Scrolling', 'Scroll left'),
                    ['Left', 'KP_Left']
                ),
            'scroll_right':
                MAP(
                    INFO('Scrolling', 'Scroll right'),
                    ['Right', 'KP_Right']
                ),
            'scroll_up':
                MAP(
                    INFO('Scrolling', 'Scroll up'),
                    ['Up', 'KP_Up']
                ),

            # View
            'zoom_original':
                MAP(
                    INFO('Zoom', 'Normal size'),
                    ['<Control>0', 'KP_0']
                ),
            'zoom_in':
                MAP(
                    INFO('Zoom', 'Zoom in'),
                    ['plus', 'KP_Add', 'equal']
                ),
            'zoom_out':
                MAP(
                    INFO('Zoom', 'Zoom out'),
                    ['minus', 'KP_Subtract']
                ),

            # Zoom out is already defined as GTK menu hotkey
            'keep_transformation':
                MAP(
                    INFO('Transformation', 'Keep transformation'),
                    ['k']
                ),
            'rotate_90':
                MAP(
                    INFO('Transformation', 'Rotate 90 degrees'),
                    ['r']
                ),
            'rotate_180':
                MAP(
                    INFO('Transformation', 'Rotate 180 degrees'),
                    []
                ),
            'rotate_270':
                MAP(
                    INFO('Transformation', 'Rotate 270 degrees'),
                    ['<Shift>r']
                ),
            'flip_horiz':
                MAP(
                    INFO('Transformation', 'Flip horizontally'),
                    []
                ),
            'flip_vert':
                MAP(
                    INFO('Transformation', 'Flip vertically'),
                    []
                ),
            'no_autorotation':
                MAP(
                    INFO('Transformation', 'Never autorotate'),
                    []
                ),

            # Autorotate
            'rotate_90_width':
                MAP(
                    INFO('Autorotate', 'Rotate width 90 degrees'),
                    []
                ),
            'rotate_270_width':
                MAP(
                    INFO('Autorotate', 'Rotate width 270 degrees'),
                    []
                ),
            'rotate_90_height':
                MAP(
                    INFO('Autorotate', 'Rotate height 90 degrees'),
                    []
                ),
            'rotate_270_height':
                MAP(
                    INFO('Autorotate', 'Rotate height 270 degrees'),
                    []
                ),

            # View mode
            'double_page':
                MAP(
                    INFO('View mode', 'Double page mode'),
                    ['d']
                ),
            'manga_mode':
                MAP(
                    INFO('View mode', 'Manga mode'),
                    ['m']
                ),
            'lens':
                MAP(
                    INFO('View mode', 'Magnifying lens'),
                    ['l']
                ),
            'stretch':
                MAP(
                    INFO('View mode', 'Stretch small images'),
                    ['y']
                ),

            # Fit mode
            'best_fit_mode':
                MAP(
                    INFO('Page fit mode', 'Best fit mode'),
                    ['b']
                ),
            'fit_width_mode':
                MAP(
                    INFO('Page fit mode', 'Fit width mode'),
                    ['w']
                ),
            'fit_height_mode':
                MAP(
                    INFO('Page fit mode', 'Fit height mode'),
                    ['h']
                ),
            'fit_size_mode':
                MAP(
                    INFO('Page fit mode', 'Fit size mode'),
                    ['s']
                ),
            'fit_manual_mode':
                MAP(
                    INFO('Page fit mode', 'Manual zoom mode'),
                    ['a']
                ),

            # General UI
            'exit_fullscreen':
                MAP(
                    INFO('User interface', 'Exit from fullscreen'),
                    ['Escape']
                ),
            'fullscreen':
                MAP(
                    INFO('User interface', 'Fullscreen'),
                    ['f', 'F11']
                ),
            'minimize':
                MAP(
                    INFO('User interface', 'Minimize'),
                    ['n']
                ),
            'hide_all':
                MAP(
                    INFO('User interface', 'Show/hide all'),
                    ['i']
                ),
            'menubar':
                MAP(
                    INFO('User interface', 'Show/hide menubar'),
                    ['<Control>M']
                ),
            'scrollbar':
                MAP(
                    INFO('User interface', 'Show/hide scrollbars'),
                    []
                ),
            'statusbar':
                MAP(
                    INFO('User interface', 'Show/hide statusbar'),
                    []
                ),
            'thumbnails':
                MAP(
                    INFO('User interface', 'Thumbnails'),
                    ['F9']
                ),

            # File operations
            'close':
                MAP(
                    INFO('File', 'Close'),
                    ['<Control>W']
                ),
            'delete':
                MAP(
                    INFO('File', 'Delete'),
                    ['Delete']
                ),
            'enhance_image':
                MAP(
                    INFO('File', 'Enhance image'),
                    ['e']
                ),
            'extract_page':
                MAP(
                    INFO('File', 'Extract Page'),
                    ['<Control><Shift>s']
                ),
            'move_file':
                MAP(
                    INFO('File', 'Move to subdirectory'),
                    ['Insert', 'grave']
                ),
            'open':
                MAP(
                    INFO('File', 'Open'),
                    ['<Control>O']
                ),
            'preferences':
                MAP(
                    INFO('File', 'Preferences'),
                    ['F12']
                ),
            'properties':
                MAP(
                    INFO('File', 'Properties'),
                    ['<Alt>Return']
                ),
            'quit':
                MAP(
                    INFO('File', 'Quit'),
                    ['<Control>Q']
                ),
            'refresh_archive':
                MAP(
                    INFO('File', 'Refresh'),
                    ['<control><shift>R']
                ),
        }


KeyBindingsMap = _KeyBindingsMap()
