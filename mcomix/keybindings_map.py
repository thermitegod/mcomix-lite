# -*- coding: utf-8 -*-

#: Bindings defined in this dictionary will appear in the configuration dialog.
#: If 'group' is None, the binding cannot be modified from the preferences dialog.

class _KeyBindingsInfo:
    def __init__(self):
        super().__init__()

        self.BINDING_INFO = {
            # Navigation between pages, archives, directories
            'previous_page': {'title': 'Previous page', 'group': 'Navigation'},
            'next_page': {'title': 'Next page', 'group': 'Navigation'},
            'previous_page_ff': {'title': 'Back ten pages', 'group': 'Navigation'},
            'next_page_ff': {'title': 'Forward ten pages', 'group': 'Navigation'},
            'previous_page_singlestep': {'title': 'Previous page (always one page)', 'group': 'Navigation'},
            'next_page_singlestep': {'title': 'Next page (always one page)', 'group': 'Navigation'},

            'first_page': {'title': 'First page', 'group': 'Navigation'},
            'last_page': {'title': 'Last page', 'group': 'Navigation'},
            'go_to': {'title': 'Go to page', 'group': 'Navigation'},

            'next_archive': {'title': 'Next archive', 'group': 'Navigation'},
            'previous_archive': {'title': 'Previous archive', 'group': 'Navigation'},
            'next_directory': {'title': 'Next directory', 'group': 'Navigation'},
            'previous_directory': {'title': 'Previous directory', 'group': 'Navigation'},

            # Scrolling
            'scroll_down': {'title': 'Scroll down', 'group': 'Scroll'},
            'scroll_up': {'title': 'Scroll up', 'group': 'Scroll'},
            'scroll_right': {'title': 'Scroll right', 'group': 'Scroll'},
            'scroll_left': {'title': 'Scroll left', 'group': 'Scroll'},

            # View
            'zoom_in': {'title': 'Zoom in', 'group': 'Zoom'},
            'zoom_out': {'title': 'Zoom out', 'group': 'Zoom'},
            'zoom_original': {'title': 'Normal size', 'group': 'Zoom'},

            'keep_transformation': {'title': 'Keep transformation', 'group': 'Transformation'},
            'rotate_90': {'title': 'Rotate 90 degrees CW', 'group': 'Transformation'},
            'rotate_180': {'title': 'Rotate 180 degrees', 'group': 'Transformation'},
            'rotate_270': {'title': 'Rotate 90 degrees CCW', 'group': 'Transformation'},
            'flip_horiz': {'title': 'Flip horizontally', 'group': 'Transformation'},
            'flip_vert': {'title': 'Flip vertically', 'group': 'Transformation'},
            'no_autorotation': {'title': 'Never autorotate', 'group': 'Transformation'},

            'rotate_90_width': {'title': 'Rotate width 90 degrees CW', 'group': 'Autorotate by width'},
            'rotate_270_width': {'title': 'Rotate width 90 degrees CCW', 'group': 'Autorotate by width'},
            'rotate_90_height': {'title': 'Rotate height 90 degrees CW', 'group': 'Autorotate by height'},
            'rotate_270_height': {'title': 'Rotate height 90 degrees CCW', 'group': 'Autorotate by height'},

            'double_page': {'title': 'Double page mode', 'group': 'View mode'},
            'manga_mode': {'title': 'Manga mode', 'group': 'View mode'},

            'lens': {'title': 'Magnifying lens', 'group': 'View mode'},
            'stretch': {'title': 'Stretch small images', 'group': 'View mode'},

            'best_fit_mode': {'title': 'Best fit mode', 'group': 'View mode'},
            'fit_width_mode': {'title': 'Fit width mode', 'group': 'View mode'},
            'fit_height_mode': {'title': 'Fit height mode', 'group': 'View mode'},
            'fit_size_mode': {'title': 'Fit size mode', 'group': 'View mode'},
            'fit_manual_mode': {'title': 'Manual zoom mode', 'group': 'View mode'},

            # General UI
            'exit_fullscreen': {'title': 'Exit from fullscreen', 'group': 'User interface'},

            'minimize': {'title': 'Minimize', 'group': 'User interface'},
            'fullscreen': {'title': 'Fullscreen', 'group': 'User interface'},
            'menubar': {'title': 'Show/hide menubar', 'group': 'User interface'},
            'statusbar': {'title': 'Show/hide statusbar', 'group': 'User interface'},
            'scrollbar': {'title': 'Show/hide scrollbars', 'group': 'User interface'},
            'thumbnails': {'title': 'Thumbnails', 'group': 'User interface'},
            'hide_all': {'title': 'Show/hide all', 'group': 'User interface'},

            # File operations
            'move_file': {'title': 'Move to subdirectory', 'group': 'File'},
            'delete': {'title': 'Delete', 'group': 'File'},
            'refresh_archive': {'title': 'Refresh', 'group': 'File'},
            'close': {'title': 'Close', 'group': 'File'},
            'quit': {'title': 'Quit', 'group': 'File'},
            'extract_page': {'title': 'Save As', 'group': 'File'},

            'properties': {'title': 'Properties', 'group': 'File'},
            'preferences': {'title': 'Preferences', 'group': 'File'},

            'open': {'title': 'Open', 'group': 'File'},
            'enhance_image': {'title': 'Enhance image', 'group': 'File'},
        }


class _KeyBindingsDefault:
    def __init__(self):
        super().__init__()

        self.DEFAULT_BINDINGS = {
            # Navigation between pages, archives, directories
            'previous_page': ['Page_Up', 'KP_Page_Up', 'BackSpace'],
            'next_page': ['Page_Down', 'KP_Page_Down'],
            'previous_page_singlestep': ['<Primary>Up', '<Primary>Page_Up', '<Primary>KP_Page_Up'],
            'next_page_singlestep': ['<Primary>Down', '<Primary>Page_Down', '<Primary>KP_Page_Down'],
            'previous_page_ff': ['<Shift>Page_Up', '<Shift>KP_Page_Up', '<Shift>BackSpace', '<Shift><Mod1>Left'],
            'next_page_ff': ['<Shift>Page_Down', '<Shift>KP_Page_Down', '<Shift><Mod1>Right'],

            'first_page': ['Home', 'KP_Home'],
            'last_page': ['End', 'KP_End'],
            'go_to': ['G'],

            'next_archive': ['<Primary>Right'],
            'previous_archive': ['<Primary>Left'],
            'next_directory': ['<control>N'],
            'previous_directory': ['<control>P'],

            # Scrolling
            # Arrow keys scroll the image
            'scroll_down': ['Down', 'KP_Down'],
            'scroll_up': ['Up', 'KP_Up'],
            'scroll_right': ['Right', 'KP_Right'],
            'scroll_left': ['Left', 'KP_Left'],

            # View
            'zoom_in': ['plus', 'KP_Add', 'equal'],
            'zoom_out': ['minus', 'KP_Subtract'],
            'zoom_original': ['<Control>0', 'KP_0'],

            # Zoom out is already defined as GTK menu hotkey
            'keep_transformation': ['k'],
            'rotate_90': ['r'],
            'rotate_270': ['<Shift>r'],
            'rotate_180': [],
            'flip_horiz': [],
            'flip_vert': [],
            'no_autorotation': [],

            'rotate_90_width': [],
            'rotate_270_width': [],
            'rotate_90_height': [],
            'rotate_270_height': [],

            'double_page': ['d'],
            'manga_mode': ['m'],

            'lens': ['l'],
            'stretch': ['y'],

            'best_fit_mode': ['b'],
            'fit_width_mode': ['w'],
            'fit_height_mode': ['h'],
            'fit_size_mode': ['s'],
            'fit_manual_mode': ['a'],

            # General UI
            'exit_fullscreen': ['Escape'],

            'minimize': ['n'],
            'fullscreen': ['f', 'F11'],
            'menubar': ['<Control>M'],
            'statusbar': [],
            'scrollbar': [],
            'thumbnails': ['F9'],
            'hide_all': ['i'],

            # File operations
            'delete': ['Delete'],
            'refresh_archive': ['<control><shift>R'],
            'close': ['<Control>W'],
            'quit': ['<Control>Q'],
            'extract_page': ['<Control><Shift>s'],
            'move_file': ['Insert', 'grave'],

            'properties': ['<Alt>Return'],
            'preferences': ['F12'],

            'open': ['<Control>O'],
            'enhance_image': ['e'],
        }


KeyBindingsInfo = _KeyBindingsInfo()
KeyBindingsDefault = _KeyBindingsDefault()
