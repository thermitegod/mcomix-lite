# -*- coding: utf-8 -*-

"""preferences_dialog.py - Preferences dialog"""

import PIL.Image  # for PIL interpolation prefs
from gi.repository import GObject, GdkPixbuf, Gtk

from mcomix.constants import Constants
from mcomix.keybindings_editor import KeybindingEditorWindow
from mcomix.preferences import config
from mcomix.preferences_page import PreferencePage


class _PreferencesDialog(Gtk.Dialog):
    """
    The preferences dialog where most (but not all) settings that are
    saved between sessions are presented to the user
    """

    def __init__(self, window, keybindings):
        super().__init__(title='Preferences')

        self.set_transient_for(window)

        # Button text is set later depending on active tab
        self.__reset_button = self.add_button('', Constants.RESPONSE['REVERT_TO_DEFAULT'])
        self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.__window = window
        self.set_resizable(True)
        self.set_default_response(Gtk.ResponseType.CLOSE)

        self.__keybindings = keybindings

        self.connect('response', self._response)

        self.__notebook = Gtk.Notebook()
        self.vbox.pack_start(self.__notebook, True, True, 0)
        self.set_border_width(2)
        self.__notebook.set_border_width(2)

        self.__notebook.append_page(self._init_appearance_tab(),
                                    Gtk.Label(label='Appearance'))

        self.__notebook.append_page(self._init_behaviour_tab(),
                                    Gtk.Label(label='Behaviour'))

        self.__notebook.append_page(self._init_display_tab(),
                                    Gtk.Label(label='Display'))

        self.__notebook.append_page(self._init_dialog_tab(),
                                    Gtk.Label(label='Dialog'))

        self.__notebook.append_page(self._init_animation_tab(),
                                    Gtk.Label(label='Animation'))

        self.__notebook.append_page(self._init_advanced_tab(),
                                    Gtk.Label(label='Advanced'))

        self.__shortcuts = self._init_shortcuts_tab()
        self.__notebook.append_page(self.__shortcuts,
                                    Gtk.Label(label='Shortcuts'))

        self.__notebook.connect('switch-page', self._tab_page_changed)

        self.show_all()

    def _init_appearance_tab(self):
        # ----------------------------------------------------------------
        # The "Appearance" tab.
        # ----------------------------------------------------------------
        page = PreferencePage()

        page.new_section('User Interface')

        page.add_row(self._create_pref_check_button(
            'Escape key closes program',
            'ESCAPE_QUITS'))

        page.new_section('Thumbnails')

        page.add_row(self._create_pref_check_button(
            'Show page numbers on thumbnails',
            'SHOW_PAGE_NUMBERS_ON_THUMBNAILS'))

        page.add_row(self._create_pref_check_button(
            'Use archive thumbnail as application icon',
            'ARCHIVE_THUMBNAIL_AS_ICON'))

        page.add_row(Gtk.Label(label='Thumbnail size (pixels):'),
                     self._create_pref_spinner(
                         'THUMBNAIL_SIZE',
                         1, 20, 500, 1, 10, 0))

        page.new_section('Transparency')

        page.add_row(self._create_pref_check_button(
            'Use a checkered background for transparent images',
            'CHECKERED_BG_FOR_TRANSPARENT_IMAGES'))

        page.add_row(Gtk.Label(label='Checkered background size:'),
                     self._create_combobox_checkered_bg_size())

        return page

    def _init_behaviour_tab(self):
        # ----------------------------------------------------------------
        # The "Behaviour" tab.
        # ----------------------------------------------------------------
        page = PreferencePage()

        page.new_section('Page Flipping')

        page.add_row(self._create_pref_check_button(
            'Use western style page flipping in manga mode',
            'MANGA_FLIP_RIGHT'))

        page.add_row(self._create_pref_check_button(
            'Use manga style page flipping in western mode',
            'WESTERN_FLIP_LEFT'))

        page.new_section('Scroll')

        page.add_row(self._create_pref_check_button(
            'Flip pages with mouse wheel',
            'FLIP_WITH_WHEEL'))

        page.add_row(Gtk.Label(label='Number of pixels to scroll a page per arrow key press:'),
                     self._create_pref_spinner(
                         'PIXELS_TO_SCROLL_PER_KEY_EVENT',
                         1, 1, 500, 1, 3, 0))

        page.add_row(Gtk.Label(label='Number of pixels to scroll a page per mouse wheel turn:'),
                     self._create_pref_spinner(
                         'PIXELS_TO_SCROLL_PER_MOUSE_WHEEL_EVENT',
                         1, 1, 500, 1, 3, 0))

        page.new_section('File Opening')

        page.add_row(self._create_pref_check_button(
            'Automatically open the next archive',
            'AUTO_OPEN_NEXT_ARCHIVE'))

        page.new_section('Double Page Mode')

        page.add_row(self._create_pref_check_button(
            'Flip two pages in double page mode',
            'DOUBLE_STEP_IN_DOUBLE_PAGE_MODE'))

        page.add_row(Gtk.Label(label='Show only one page where appropriate:'),
                     self._create_combobox_doublepage_as_one())

        page.new_section('Page Selection')

        page.add_row(self._create_pref_check_button(
            'Open the first file when navigating to previous archive',
            'OPEN_FIRST_PAGE'))

        return page

    def _init_display_tab(self):
        # ----------------------------------------------------------------
        # The "Display" tab.
        # ----------------------------------------------------------------
        page = PreferencePage()

        page.new_section('Fullscreen')

        page.add_row(self._create_pref_check_button(
            'Use fullscreen by default',
            'DEFAULT_FULLSCREEN'))

        page.add_row(self._create_pref_check_button(
            'Hide all toolbars in fullscreen',
            'HIDE_ALL_IN_FULLSCREEN'))

        page.new_section('Fit To Size Mode')

        page.add_row(Gtk.Label(label='Fit to width or height:'),
                     self._create_combobox_fitmode())

        page.add_row(Gtk.Label(label='Fixed size for this mode:'),
                     self._create_pref_spinner(
                         'FIT_TO_SIZE_PX',
                         1, 10, 10000, 10, 50, 0))

        page.new_section('Rotation')

        page.add_row(self._create_pref_check_button(
            'Rotate images according to their metadata',
            'AUTO_ROTATE_FROM_EXIF'))

        page.new_section('Image Quality')

        page.add_row(Gtk.Label(label='Scaling mode'),
                     self._create_combobox_scaling_quality())

        page.new_section('Advanced filters')

        page.add_row(Gtk.Label(label='High-quality scaling for main area'),
                     self._create_combobox_pil_scaling_filter())

        page.new_section('Statusbar')

        page.add_row(self._create_pref_check_button(
            'Show full path of current file in statusbar',
            'STATUSBAR_FULLPATH'))

        page.add_row(self._create_pref_check_button(
            'Show page scaling percent',
            'STATUSBAR_SHOW_SCALE'))

        page.add_row(Gtk.Label(label='Charactor to use as statusbar separator'),
                     self._create_pref_text_box('STATUSBAR_SEPARATOR'))

        page.new_section('Bookmarks')

        page.add_row(self._create_pref_check_button(
            'Show bookmark path in bookmark menu',
            'BOOKMARK_SHOW_PATH'))

        page.new_section('Cursor')

        page.add_row(self._create_pref_check_button(
            'Hide cursor after delay',
            'HIDE_CURSOR'))

        return page

    def _init_dialog_tab(self):
        # ----------------------------------------------------------------
        # The "Display" tab.
        # ----------------------------------------------------------------
        page = PreferencePage()

        page.new_section('Bookmark')

        page.add_row(Gtk.Label(label='Bookmark dialog size (width):'),
                     self._create_pref_spinner(
                         'BOOKMARK_WIDTH',
                         1, 480, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='Bookmark dialog size (height):'),
                     self._create_pref_spinner(
                         'BOOKMARK_HEIGHT',
                         1, 320, 10000, 10, 10, 0))

        page.new_section('Properties')

        page.add_row(Gtk.Label(label='Properties dialog size (width):'),
                     self._create_pref_spinner(
                         'PROPERTIES_WIDTH',
                         1, 480, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='Properties dialog size (height):'),
                     self._create_pref_spinner(
                         'PROPERTIES_HEIGHT',
                         1, 320, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='Properties thumb size:'),
                     self._create_pref_spinner(
                         'PROPERTIES_THUMB_SIZE',
                         1, 32, 1024, 1, 10, 0))

        page.new_section('Page Selector')

        page.add_row(Gtk.Label(label='window size (width):'),
                     self._create_pref_spinner(
                         'PAGESELECTOR_WIDTH',
                         1, 560, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='window size (height):'),
                     self._create_pref_spinner(
                         'PAGESELECTOR_HEIGHT',
                         1, 820, 10000, 10, 10, 0))

        page.new_section('Main Window')

        page.add_row(self._create_pref_check_button(
            'Save window size',
            'WINDOW_SAVE'))

        page.add_row(Gtk.Label(label='window size (width):'),
                     self._create_pref_spinner(
                         'WINDOW_WIDTH',
                         1, 480, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='window size (height):'),
                     self._create_pref_spinner(
                         'WINDOW_HEIGHT',
                         1, 320, 10000, 10, 10, 0))

        return page

    def _init_animation_tab(self):
        # ----------------------------------------------------------------
        # The "Animation" tab.
        # ----------------------------------------------------------------
        page = PreferencePage()

        page.new_section('Animated Images')

        page.add_row(Gtk.Label(label='Animation Mode'),
                     self._create_combobox_animation_mode())

        page.add_row(self._create_pref_check_button(
            'Use animation background (otherwise uses Appearance -> Background)',
            'ANIMATION_BACKGROUND'))

        page.add_row(self._create_pref_check_button(
            'Enable scale, rotate, flip and enhance operation on animation',
            'ANIMATION_TRANSFORM'))

        return page

    def _init_advanced_tab(self):
        # ----------------------------------------------------------------
        # The "Advanced" tab.
        # ----------------------------------------------------------------
        page = PreferencePage()

        page.new_section('File Order')

        page.add_row(Gtk.Label(label='Sort files and directories by:'),
                     self._create_combobox_sort_by())

        page.add_row(Gtk.Label(label='Sort archives by:'),
                     self._create_combobox_archive_sort_by())

        page.new_section('Moving Files')

        page.add_row(Gtk.Label(label='Move file location (must be relative)'),
                     self._create_pref_text_box('MOVE_FILE'))

        page.new_section('Extraction And Cache')

        page.add_row(Gtk.Label(label='Maximum number of pages to store in the cache:'),
                     self._create_pref_spinner(
                         'MAX_PAGES_TO_CACHE',
                         1, 2, 10000, 1, 3, 0))

        page.new_section('Magnifying Lens')

        page.add_row(Gtk.Label(label='Magnifying lens size (in pixels):'),
                     self._create_pref_spinner(
                         'LENS_SIZE',
                         1, 50, 400, 1, 10, 0))

        page.add_row(Gtk.Label(label='Magnification lens factor:'),
                     self._create_pref_spinner(
                         'LENS_MAGNIFICATION',
                         1, 1.1, 10.0, 0.1, 1.0, 1))

        page.new_section('Enhance')

        page.add_row(self._create_pref_check_button(
            'Show extra info on enhance dialog',
            'ENHANCE_EXTRA'))

        page.new_section('Unit Size')

        page.add_row(self._create_pref_check_button(
            'Show filesize in SI unit size 10^3 instead of 2^10',
            'SI_UNITS'))

        page.new_section('Threads')

        page.add_row(Gtk.Label(label='Maximum number of threads:'),
                     self._create_pref_spinner(
                         'MAX_THREADS',
                         1, 1, 128, 1, 4, 0))

        return page

    def _init_shortcuts_tab(self):
        # ----------------------------------------------------------------
        # The "Shortcuts" tab.
        # ----------------------------------------------------------------
        page = KeybindingEditorWindow(self.__keybindings)

        return page

    def _tab_page_changed(self, notebook, page_ptr, page_num: int):
        """
        Dynamically switches the "Reset" button's text
        depending on the currently selected tab page
        """

        if notebook.get_nth_page(page_num) == self.__shortcuts:
            self.__reset_button.set_label('_Reset keys')
            self.__reset_button.set_sensitive(True)
        else:
            self.__reset_button.set_label('Clear _dialog choices')
            self.__reset_button.set_sensitive(len(config['STORED_DIALOG_CHOICES']) > 0)

    def _response(self, dialog, response):
        if response == Gtk.ResponseType.CLOSE:
            PreferenceDialog.close_dialog()

        elif response == Constants.RESPONSE['REVERT_TO_DEFAULT']:
            if self.__notebook.get_nth_page(self.__notebook.get_current_page()) == self.__shortcuts:
                # "Shortcuts" page is active, reset all keys to their default value
                self.__keybindings.clear_all()
                self.__window.get_event_handler().register_key_events()
                self.__keybindings.write_keybindings_file()
                self.__shortcuts.refresh_model()
            else:
                # Reset stored choices
                config['STORED_DIALOG_CHOICES'] = {}
                self.__reset_button.set_sensitive(False)

        else:
            # Other responses close the dialog, e.g. clicking the X icon on the dialog.
            PreferenceDialog.close_dialog()

    def _create_combobox_checkered_bg_size(self):
        """
        Creates combo box to set box size for alpha images
        """

        items = (
            ('2', 2),
            ('4', 4),
            ('8', 8),
            ('16', 16),
            ('32', 32),
            ('64', 64),
            ('128', 128),
            ('256', 256),
            ('512', 512),
        )

        return self._create_combobox(items, 'CHECKERED_BG_SIZE')

    def _create_combobox_doublepage_as_one(self):
        """
        Creates the ComboBox control for selecting virtual double page options
        """

        items = (
            ('Never', Constants.DOUBLE_PAGE['NEVER']),
            ('Only for title pages', Constants.DOUBLE_PAGE['AS_ONE_TITLE']),
            ('Only for wide images', Constants.DOUBLE_PAGE['AS_ONE_WIDE']),
            ('Always', Constants.DOUBLE_PAGE['AS_ONE_TITLE'] |
             Constants.DOUBLE_PAGE['AS_ONE_WIDE']))

        return self._create_combobox(items, 'VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES')

    def _create_combobox_fitmode(self):
        """Combobox for fit to size mode"""
        items = (
            ('Fit to width', Constants.ZOOM['WIDTH']),
            ('Fit to height', Constants.ZOOM['HEIGHT']))

        return self._create_combobox(items, 'FIT_TO_SIZE_MODE')

    def _create_combobox_sort_by(self):
        """
        Creates the ComboBox control for selecting file sort by options
        """

        sortkey_items = (
            ('No sorting', Constants.FILE_SORT_TYPE['NONE']),
            ('File name', Constants.FILE_SORT_TYPE['NAME']),
            ('File size', Constants.FILE_SORT_TYPE['SIZE']),
            ('Last modified', Constants.FILE_SORT_TYPE['LAST_MODIFIED']))

        sortkey_box = self._create_combobox(sortkey_items, 'SORT_BY')

        sortorder_items = (
            ('Ascending', Constants.FILE_SORT_DIRECTION['ASCENDING']),
            ('Descending', Constants.FILE_SORT_DIRECTION['DESCENDING']))

        sortorder_box = self._create_combobox(sortorder_items, 'SORT_ORDER')

        box = Gtk.HBox()
        box.pack_start(sortkey_box, True, True, 0)
        box.pack_start(sortorder_box, True, True, 0)

        return box

    def _create_combobox_archive_sort_by(self):
        """
        Creates the ComboBox control for selecting archive sort by options
        """

        sortkey_items = (
            ('No sorting', Constants.FILE_SORT_TYPE['NONE']),
            ('Natural order', Constants.FILE_SORT_TYPE['NAME']),
            ('Literal order', Constants.FILE_SORT_TYPE['NAME_LITERAL']))

        sortkey_box = self._create_combobox(sortkey_items, 'SORT_ARCHIVE_BY')

        sortorder_items = (
            ('Ascending', Constants.FILE_SORT_DIRECTION['ASCENDING']),
            ('Descending', Constants.FILE_SORT_DIRECTION['DESCENDING']))

        sortorder_box = self._create_combobox(sortorder_items, 'SORT_ARCHIVE_ORDER')

        box = Gtk.HBox()
        box.pack_start(sortkey_box, True, True, 0)
        box.pack_start(sortorder_box, True, True, 0)

        return box

    def _create_combobox_scaling_quality(self):
        """
        Creates combo box for image scaling quality
        """

        items = (
            ('Nearest (very fast)', int(GdkPixbuf.InterpType.NEAREST)),
            ('Tiles (fast)', int(GdkPixbuf.InterpType.TILES)),
            ('Bilinear (normal)', int(GdkPixbuf.InterpType.BILINEAR))
        )

        return self._create_combobox(items, 'SCALING_QUALITY')

    def _create_combobox_pil_scaling_filter(self):
        """
        Creates combo box for PIL filter to scale with in main view
        """

        items = (
            # -1 defers to 'scaling quality'
            ('None', -1),
            # PIL 0
            ('Nearest', PIL.Image.NEAREST),
            # PIL 1
            ('Lanczos', PIL.Image.LANCZOS),
            # PIL 2
            ('Bilinear', PIL.Image.BILINEAR),
            # PIL 3
            ('Bicubic', PIL.Image.BICUBIC),
            # PIL 4
            ('Box', PIL.Image.BOX),
            # PIL 5
            ('Hamming', PIL.Image.HAMMING),
        )

        return self._create_combobox(items, 'PIL_SCALING_FILTER')

    def _create_combobox_animation_mode(self):
        """
        Creates combo box for animation mode
        """

        items = (
            ('Never', Constants.ANIMATION['DISABLED']),
            ('Normal', Constants.ANIMATION['NORMAL']),
            ('Once', Constants.ANIMATION['ONCE']),
            ('Infinity', Constants.ANIMATION['INF']),
        )

        return self._create_combobox(items, 'ANIMATION_MODE')

    def _changed_cb(self, combobox, preference: str):
        """
        Called whenever cb box has been changed
        """

        _iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(_iter):
            value = combobox.get_model().get_value(_iter, 1)
            last_value = config[preference]
            config[preference] = value

            if value != last_value:
                if preference in ('ANIMATION_MODE', 'SORT_ARCHIVE_ORDER',
                                  'SORT_ARCHIVE_BY', 'SORT_ORDER', 'SORT_BY'):
                    self.__window.filehandler.refresh_file()
                elif preference in ('PIL_SCALING_FILTER', 'SCALING_QUALITY',
                                    'VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES'):
                    if preference in ('PIL_SCALING_FILTER', 'SCALING_QUALITY'):
                        self.__window.statusbar.update_image_scaling()
                    self.__window.draw_image()
                elif preference in ('FIT_TO_SIZE_MODE',):
                    self.__window.change_zoom_mode()
                elif preference in ('CHECKERED_BG_SIZE',):
                    self.__window.draw_image()

    def _create_combobox(self, options: tuple, preference: str):
        """
        Creates a new dropdown combobox and populates it with the items passed in C{options}.

        :param options: List of tuples: (Option display text, option value)
        :param preference: One of the values passed in C{options} that will
            be pre-selected when the control is created.
        :returns: Gtk.ComboBox
        """

        # Use the first list item to determine typing of model fields.
        # First field is textual description, second field is value.
        model = Gtk.ListStore(GObject.TYPE_STRING, type(options[0][1]))
        for text, value in options:
            model.append((text, value))

        box = Gtk.ComboBox(model=model)
        renderer = Gtk.CellRendererText()
        box.pack_start(renderer, True)
        box.add_attribute(renderer, 'text', 0)

        # Set active box option
        _iter = model.get_iter_first()
        while _iter:
            if model.get_value(_iter, 1) == config[preference]:
                box.set_active_iter(_iter)
                break
            else:
                _iter = model.iter_next(_iter)

        box.connect('changed', self._changed_cb, preference)

        return box

    def _create_pref_check_button(self, label: str, prefkey: str):
        button = Gtk.CheckButton(label=label)
        button.set_active(config[prefkey])
        button.connect('toggled', self._check_button_cb, prefkey)
        return button

    def _check_button_cb(self, button, preference: str):
        """
        Callback for all checkbutton-type preferences
        """

        config[preference] = button.get_active()

        if (preference in ('CHECKERED_BG_FOR_TRANSPARENT_IMAGES', 'AUTO_ROTATE_FROM_EXIF')) or \
                (preference in ('HIDE_ALL_IN_FULLSCREEN',) and self.__window.is_fullscreen):
            self.__window.draw_image()

        elif preference in ('ANIMATION_BACKGROUND', 'ANIMATION_TRANSFORM'):
            self.__window.thumbnailsidebar.toggle_page_numbers_visible()
            self.__window.filehandler.refresh_file()

        elif preference in ('OPEN_FIRST_PAGE', ):
            self.__window.filehandler.update_opening_behavior()

    def _create_pref_spinner(self, prefkey: str, scale: float, lower: float, upper: float,
                             step_incr: float, page_incr: float, digits: float):
        value = config[prefkey] / scale
        adjustment = Gtk.Adjustment(value=value, lower=lower, upper=upper, step_increment=step_incr,
                                    page_increment=page_incr)
        spinner = Gtk.SpinButton.new(adjustment, 0.0, digits)
        spinner.set_size_request(80, -1)
        spinner.connect('value_changed', self._spinner_cb, prefkey)
        return spinner

    def _spinner_cb(self, spinbutton, preference: str):
        """
        Callback for spinner-type preferences
        """

        value = spinbutton.get_value()

        if preference in ('LENS_MAGNIFICATION',):
            config[preference] = float(value)
        else:
            config[preference] = int(value)

        #  now apply new pref
        if preference in ('THUMBNAIL_SIZE',):
            self.__window.thumbnailsidebar.resize()
            self.__window.draw_image()
        elif preference in ('MAX_PAGES_TO_CACHE',):
            self.__window.imagehandler.do_cacheing()
        elif preference in ('FIT_TO_SIZE_PX',):
            self.__window.change_zoom_mode()

    @staticmethod
    def _create_pref_text_box(preference: str):
        def save_pref_text_box(text):
            config[preference] = text.get_text()

        box = Gtk.Entry()
        box.set_text(config[preference])
        box.connect('changed', save_pref_text_box)
        return box


class _PreferenceDialog:
    def __init__(self):
        super().__init__()

        self.__dialog = None

        self.__window = None
        self.__keybindings = None

    def open_dialog(self, event, data):
        """
        Create and display the preference dialog
        """

        self.__window = data[0]
        self.__keybindings = data[1]

        # if the dialog window is not created then create the window
        if self.__dialog is None:
            self.__dialog = _PreferencesDialog(self.__window, self.__keybindings)
        else:
            # if the dialog window already exists bring it to the forefront of the screen
            self.__dialog.present()

    def close_dialog(self):
        # if the dialog window exists then destroy it
        if self.__dialog is not None:
            self.__dialog.destroy()
            self.__dialog = None


PreferenceDialog = _PreferenceDialog()


