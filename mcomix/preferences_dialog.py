# -*- coding: utf-8 -*-

"""preferences_dialog.py - Preferences dialog"""

from gi.repository import GObject, Gtk

from mcomix.enum.animation import Animation
from mcomix.enum.double_page import DoublePage
from mcomix.enum.file_sort import FileSortDirection, FileSortType
from mcomix.enum.image_scaling import ScalingGDK, ScalingPIL
from mcomix.enum.zoom_modes import ZoomModes
from mcomix.keybindings_editor import KeybindingEditorWindow
from mcomix.preferences import config
from mcomix.preferences_page import PreferencePage


class PreferencesDialog(Gtk.Dialog):
    """
    The preferences dialog where most (but not all) settings that are
    saved between sessions are presented to the user
    """

    def __init__(self, window):
        super().__init__(title='Preferences')

        self.set_modal(True)
        self.set_transient_for(window)

        # Button text is set later depending on active tab
        self.__reset_button = self.add_button('', Gtk.ResponseType.REJECT)
        self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.__window = window
        self.set_resizable(True)
        self.set_default_response(Gtk.ResponseType.CLOSE)

        self.__keybindings = self.__window.keybindings

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

        page.new_section('Manga Mode')

        page.add_row(self._create_pref_check_button(
            'Default manga mode',
            'DEFAULT_MANGA_MODE'))

        page.new_section('Double Page Mode')

        page.add_row(self._create_pref_check_button(
            'Default double page mode',
            'DEFAULT_DOUBLE_PAGE'))

        page.add_row(self._create_pref_check_button(
            'Flip two pages in double page mode',
            'DOUBLE_STEP_IN_DOUBLE_PAGE_MODE'))

        page.add_row(Gtk.Label(label='Show only one page where appropriate:'),
                     self._create_combobox_doublepage_as_one())

        page.new_section('Page Selection')

        page.add_row(self._create_pref_check_button(
            'Start at the first page when opening a previous archive',
            'OPEN_FIRST_PAGE'))

        page.add_row(Gtk.Label(label='Total pages to change when using ff:'),
                     self._create_pref_spinner(
                         'PAGE_FF_STEP',
                         1, 1, 100, 1, 3, 0))

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
            'Hide the statusbar in fullscreen',
            'FULLSCREEN_HIDE_STATUSBAR'))

        page.add_row(self._create_pref_check_button(
            'Hide the menubar in fullscreen',
            'FULLSCREEN_HIDE_MENUBAR'))

        page.new_section('Fit To Size Mode')

        page.add_row(Gtk.Label(label='Page zoom mode:'),
                     self._create_combobox_zoom_mode())

        page.add_row(Gtk.Label(label='Fit to width or height:'),
                     self._create_combobox_fitmode())

        page.add_row(self._create_pref_check_button(
            'Stretch small images',
            'STRETCH'))

        page.add_row(Gtk.Label(label='Fixed size for this mode:'),
                     self._create_pref_spinner(
                         'FIT_TO_SIZE_PX',
                         1, 10, 10000, 10, 50, 0))

        page.new_section('Rotation')

        page.add_row(self._create_pref_check_button(
            'Keep manual rotation on page change',
            'KEEP_TRANSFORMATION'))

        page.add_row(self._create_pref_check_button(
            'Rotate images according to their metadata',
            'AUTO_ROTATE_FROM_EXIF'))

        page.new_section('Image Quality')

        page.add_row(Gtk.Label(label='Scaling mode'),
                     self._create_combobox_scaling_quality())

        page.new_section('Advanced filters')

        page.add_row(self._create_pref_check_button(
            'Enable PIL image scaling',
            'ENABLE_PIL_SCALING'))

        page.add_row(Gtk.Label(label='PIL image scaling mode'),
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

        page.add_row(Gtk.Label(label='Statusbar margin padding:'),
                     self._create_pref_spinner(
                         'STATUSBAR_MARGIN_PADDING',
                         1, 0, 10, 1, 3, 0))

        page.new_section('Bookmarks')

        page.add_row(self._create_pref_check_button(
            'Show bookmark path in bookmark menu',
            'BOOKMARK_SHOW_PATH'))

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

        page.new_section('Page Cache')

        page.add_row(Gtk.Label(label='Pages to cache ahead of current page:'),
                     self._create_pref_spinner(
                         'PAGE_CACHE_FORWARD',
                         1, 1, 50, 1, 3, 0))

        page.add_row(Gtk.Label(label='Pages to cache behind the current page:'),
                     self._create_pref_spinner(
                         'PAGE_CACHE_BEHIND',
                         1, 1, 10, 1, 3, 0))

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
        page = KeybindingEditorWindow(self.__window)

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
        if response == Gtk.ResponseType.REJECT:
            if self.__notebook.get_nth_page(self.__notebook.get_current_page()) == self.__shortcuts:
                # "Shortcuts" page is active, reset all keys to their default value
                self.__keybindings.reset_keybindings()
                self.__window.get_event_handler().register_key_events()
                self.__keybindings.write_keybindings_file()
                self.__shortcuts.refresh_model()
            else:
                # Reset stored choices
                config['STORED_DIALOG_CHOICES'] = {}
                self.__reset_button.set_sensitive(False)

        else:
            # Other responses close the dialog, e.g. clicking the X icon on the dialog.
            self.destroy()

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

    def _create_combobox_zoom_mode(self):
        """
        Creates combo box to set box size for alpha images
        """

        items = (
            ('Best fit', ZoomModes.BEST.value),
            ('Fit to width', ZoomModes.WIDTH.value),
            ('Fit to height', ZoomModes.HEIGHT.value),
            ('Fit to size', ZoomModes.SIZE.value),
            ('Manual fit', ZoomModes.MANUAL.value),
        )

        return self._create_combobox(items, 'ZOOM_MODE')

    def _create_combobox_doublepage_as_one(self):
        """
        Creates the ComboBox control for selecting virtual double page options
        """

        items = (
            ('Never', DoublePage.NEVER.value),
            ('Only for title pages', DoublePage.AS_ONE_TITLE.value),
            ('Only for wide images', DoublePage.AS_ONE_WIDE.value),
            ('Always', DoublePage.ALWAYS.value))

        return self._create_combobox(items, 'VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES')

    def _create_combobox_fitmode(self):
        """Combobox for fit to size mode"""
        items = (
            ('Fit to width', ZoomModes.WIDTH.value),
            ('Fit to height', ZoomModes.HEIGHT.value))

        return self._create_combobox(items, 'FIT_TO_SIZE_MODE')

    def _create_combobox_sort_by(self):
        """
        Creates the ComboBox control for selecting file sort by options
        """

        sortkey_items = (
            ('No sorting', FileSortType.NONE.value),
            ('File name', FileSortType.NAME.value),
            ('File size', FileSortType.SIZE.value),
            ('Last modified', FileSortType.LAST_MODIFIED.value))

        sortkey_box = self._create_combobox(sortkey_items, 'SORT_BY')

        sortorder_items = (
            ('Ascending', FileSortDirection.ASCENDING.value),
            ('Descending', FileSortDirection.DESCENDING.value))

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
            ('No sorting', FileSortType.NONE.value),
            ('Natural order', FileSortType.NAME.value),
            ('Literal order', FileSortType.NAME_LITERAL.value))

        sortkey_box = self._create_combobox(sortkey_items, 'SORT_ARCHIVE_BY')

        sortorder_items = (
            ('Ascending', FileSortDirection.ASCENDING.value),
            ('Descending', FileSortDirection.DESCENDING.value))

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
            ('Nearest', ScalingGDK.Nearest.value),
            ('Tiles', ScalingGDK.Tiles.value),
            ('Bilinear', ScalingGDK.Bilinear.value),
        )

        return self._create_combobox(items, 'GDK_SCALING_FILTER')

    def _create_combobox_pil_scaling_filter(self):
        """
        Creates combo box for PIL filter to scale with in main view
        """

        items = (
            ('Nearest', ScalingPIL.Nearest.value),
            ('Lanczos', ScalingPIL.Lanczos.value),
            ('Bilinear', ScalingPIL.Bilinear.value),
            ('Bicubic', ScalingPIL.Bicubic.value),
            ('Box', ScalingPIL.Box.value),
            ('Hamming', ScalingPIL.Hamming.value),
        )

        return self._create_combobox(items, 'PIL_SCALING_FILTER')

    def _create_combobox_animation_mode(self):
        """
        Creates combo box for animation mode
        """

        items = (
            ('Never', Animation.DISABLED.value),
            ('Normal', Animation.NORMAL.value),
            ('Once', Animation.ONCE.value),
            ('Infinity', Animation.INF.value),
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

            if value == last_value:
                return

            match preference:
                case ('ANIMATION_MODE'|'SORT_ARCHIVE_ORDER'|'SORT_ARCHIVE_BY'|'SORT_ORDER'|'SORT_BY'):
                    self.__window.filehandler.refresh_file()
                case ('PIL_SCALING_FILTER'|'GDK_SCALING_FILTER'):
                    self.__window.statusbar.update_image_scaling()
                    self.__window.draw_image()
                case ('VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES'|'CHECKERED_BG_SIZE'):
                    self.__window.draw_image()
                case ('FIT_TO_SIZE_MODE'|'ZOOM_MODE'):
                    self.__window.change_zoom_mode()

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

        match preference:
            case ('CHECKERED_BG_FOR_TRANSPARENT_IMAGES'|'AUTO_ROTATE_FROM_EXIF'):
                self.__window.draw_image()
            case ('ANIMATION_BACKGROUND'|'ANIMATION_TRANSFORM'):
                self.__window.thumbnailsidebar.toggle_page_numbers_visible()
                self.__window.filehandler.refresh_file()
            case ('OPEN_FIRST_PAGE'):
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

        if preference not in ('LENS_MAGNIFICATION',):
            config[preference] = int(value)

        match preference:
            case ('THUMBNAIL_SIZE'):
                self.__window.thumbnailsidebar.resize()
                self.__window.draw_image()
            case ('PAGE_CACHE_FORWARD'|'PAGE_CACHE_BEHIND'):
                self.__window.imagehandler.do_cacheing()
            case ('FIT_TO_SIZE_PX'):
                self.__window.change_zoom_mode()

    def _create_pref_text_box(self, preference: str):
        def save_pref_text_box(text):
            config[preference] = text.get_text()

        box = Gtk.Entry()
        box.set_text(config[preference])
        box.connect('changed', save_pref_text_box)
        return box
