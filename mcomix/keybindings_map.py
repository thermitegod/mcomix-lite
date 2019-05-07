# -*- coding: utf-8 -*-

#: Bindings defined in this dictionary will appear in the configuration dialog.
#: If 'group' is None, the binding cannot be modified from the preferences dialog.
BINDING_INFO = {
    # Navigation between pages, archives, directories
    'previous_page': {'title': 'Previous page', 'group': 'Navigation'},
    'next_page': {'title': 'Next page', 'group': 'Navigation'},
    'previous_page_ff': {'title': 'Back ten pages', 'group': 'Navigation'},
    'next_page_ff': {'title': 'Forward ten pages', 'group': 'Navigation'},
    'previous_page_dynamic': {'title': 'Previous page (dynamic)', 'group': 'Navigation'},
    'next_page_dynamic': {'title': 'Next page (dynamic)', 'group': 'Navigation'},
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
    'scroll_left_bottom': {'title': 'Scroll to bottom left', 'group': 'Scroll'},
    'scroll_middle_bottom': {'title': 'Scroll to bottom center', 'group': 'Scroll'},
    'scroll_right_bottom': {'title': 'Scroll to bottom right', 'group': 'Scroll'},

    'scroll_left_middle': {'title': 'Scroll to middle left', 'group': 'Scroll'},
    'scroll_middle': {'title': 'Scroll to center', 'group': 'Scroll'},
    'scroll_right_middle': {'title': 'Scroll to middle right', 'group': 'Scroll'},

    'scroll_left_top': {'title': 'Scroll to top left', 'group': 'Scroll'},
    'scroll_middle_top': {'title': 'Scroll to top center', 'group': 'Scroll'},
    'scroll_right_top': {'title': 'Scroll to top right', 'group': 'Scroll'},

    'scroll_down': {'title': 'Scroll down', 'group': 'Scroll'},
    'scroll_up': {'title': 'Scroll up', 'group': 'Scroll'},
    'scroll_right': {'title': 'Scroll right', 'group': 'Scroll'},
    'scroll_left': {'title': 'Scroll left', 'group': 'Scroll'},

    'smart_scroll_up': {'title': 'Smart scroll up', 'group': 'Scroll'},
    'smart_scroll_down': {'title': 'Smart scroll down', 'group': 'Scroll'},

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

    'rotate_90_width': {'title': 'Rotate 90 degrees CW', 'group': 'Autorotate by width'},
    'rotate_270_width': {'title': 'Rotate 90 degrees CCW', 'group': 'Autorotate by width'},
    'rotate_90_height': {'title': 'Rotate 90 degrees CW', 'group': 'Autorotate by height'},
    'rotate_270_height': {'title': 'Rotate 90 degrees CCW', 'group': 'Autorotate by height'},

    'double_page': {'title': 'Double page mode', 'group': 'View mode'},
    'manga_mode': {'title': 'Manga mode', 'group': 'View mode'},
    'invert_scroll': {'title': 'Invert smart scroll', 'group': 'View mode'},

    'lens': {'title': 'Magnifying lens', 'group': 'View mode'},
    'stretch': {'title': 'Stretch small images', 'group': 'View mode'},

    'best_fit_mode': {'title': 'Best fit mode', 'group': 'View mode'},
    'fit_width_mode': {'title': 'Fit width mode', 'group': 'View mode'},
    'fit_height_mode': {'title': 'Fit height mode', 'group': 'View mode'},
    'fit_size_mode': {'title': 'Fit size mode', 'group': 'View mode'},
    'fit_manual_mode': {'title': 'Manual zoom mode', 'group': 'View mode'},

    # General UI
    'exit_fullscreen': {'title': 'Exit from fullscreen', 'group': 'User interface'},

    'osd_panel': {'title': 'Show OSD panel', 'group': 'User interface'},
    'minimize': {'title': 'Minimize', 'group': 'User interface'},
    'fullscreen': {'title': 'Fullscreen', 'group': 'User interface'},
    'toolbar': {'title': 'Show/hide toolbar', 'group': 'User interface'},
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

# Generate 9 entries for executing command 1 to 9
for i in range(1, 10):
    BINDING_INFO['execute_command_%d' % i] = {
        'title': 'Execute external command' + ' (%d)' % i,
        'group': 'External commands'}

DEFAULT_BINDINGS = {
    # Navigation between pages, archives, directories
    'previous_page': ['Page_Up', 'KP_Page_Up', 'BackSpace'],
    'next_page': ['Page_Down', 'KP_Page_Down'],
    'previous_page_singlestep': ['<Primary>Up', '<Primary>Page_Up', '<Primary>KP_Page_Up'],
    'next_page_singlestep': ['<Primary>Down', '<Primary>Page_Down', '<Primary>KP_Page_Down'],
    'previous_page_dynamic': ['<Mod1>Left'],
    'next_page_dynamic': ['<Mod1>Right'],
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
    # Numpad (without numlock) aligns the image depending on the key.
    'scroll_left_bottom': ['KP_1'],
    'scroll_middle_bottom': ['KP_2'],
    'scroll_right_bottom': ['KP_3'],

    'scroll_left_middle': ['KP_4'],
    'scroll_middle': ['KP_5'],
    'scroll_right_middle': ['KP_6'],

    'scroll_left_top': ['KP_7'],
    'scroll_middle_top': ['KP_8'],
    'scroll_right_top': ['KP_9'],

    # Arrow keys scroll the image
    'scroll_down': ['Down', 'KP_Down'],
    'scroll_up': ['Up', 'KP_Up'],
    'scroll_right': ['Right', 'KP_Right'],
    'scroll_left': ['Left', 'KP_Left'],

    'smart_scroll_up': ['<Shift>space'],
    'smart_scroll_down': ['space'],

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
    'invert_scroll': ['x'],

    'lens': ['l'],
    'stretch': ['y'],

    'best_fit_mode': ['b'],
    'fit_width_mode': ['w'],
    'fit_height_mode': ['h'],
    'fit_size_mode': ['s'],
    'fit_manual_mode': ['a'],

    # General UI
    'exit_fullscreen': ['Escape'],

    'osd_panel': ['Tab'],
    'minimize': ['n'],
    'fullscreen': ['f', 'F11'],
    'toolbar': [],
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

# Execute external command. Bind keys from 1 to 9 to commands 1 to 9.
for i in range(1, 10):
    DEFAULT_BINDINGS['execute_command_%d' % i] = [str(i)]
