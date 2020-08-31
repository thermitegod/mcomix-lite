# -*- coding: utf-8 -*-

"""preferences_dialog.py - Preferences dialog"""

from gi.repository import GObject, GdkPixbuf, Gtk

from mcomix import constants
from mcomix.keybindings import KeybindingManager
from mcomix.keybindings_editor import KeybindingEditorWindow
from mcomix.labels import BoldLabel
from mcomix.preferences import prefs


class _PreferencesDialog(Gtk.Dialog):
    """
    The preferences dialog where most (but not all) settings that are
    saved between sessions are presented to the user
    """

    def __init__(self, window):
        super().__init__(title='Preferences')

        self.set_transient_for(window)

        # Button text is set later depending on active tab
        self.__reset_button = self.add_button('', constants.RESPONSE_REVERT_TO_DEFAULT)
        self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.__window = window
        self.set_resizable(True)
        self.set_default_response(Gtk.ResponseType.CLOSE)

        self.__manager = KeybindingManager.keybinding_manager(self.__window)

        self.connect('response', self._response)

        notebook = self.notebook = Gtk.Notebook()
        self.vbox.pack_start(notebook, True, True, 0)
        self.set_border_width(4)
        notebook.set_border_width(6)

        appearance = self._init_appearance_tab()
        notebook.append_page(appearance, Gtk.Label(label='Appearance'))
        behaviour = self._init_behaviour_tab()
        notebook.append_page(behaviour, Gtk.Label(label='Behaviour'))
        display = self._init_display_tab()
        notebook.append_page(display, Gtk.Label(label='Display'))
        display = self._init_dialog_tab()
        notebook.append_page(display, Gtk.Label(label='Dialog'))
        animation = self._init_animation_tab()
        notebook.append_page(animation, Gtk.Label(label='Animation'))
        advanced = self._init_advanced_tab()
        notebook.append_page(advanced, Gtk.Label(label='Advanced'))
        shortcuts = self.shortcuts = self._init_shortcuts_tab()
        notebook.append_page(shortcuts, Gtk.Label(label='Shortcuts'))

        notebook.connect('switch-page', self._tab_page_changed)

        self.show_all()

    def _init_appearance_tab(self):
        # ----------------------------------------------------------------
        # The "Appearance" tab.
        # ----------------------------------------------------------------
        page = _PreferencePage(None)

        page.new_section('User interface')

        page.add_row(self._create_pref_check_button(
                'Escape key closes program',
                'escape quits'))

        page.new_section('Thumbnails')

        page.add_row(self._create_pref_check_button(
                'Show page numbers on thumbnails',
                'show page numbers on thumbnails'))

        page.add_row(self._create_pref_check_button(
                'Use archive thumbnail as application icon',
                'archive thumbnail as icon'))

        page.add_row(Gtk.Label(label='Thumbnail size (in pixels):'),
                     self._create_pref_spinner(
                             'thumbnail size',
                             1, 20, 500, 1, 10, 0))

        page.new_section('Transparency')

        page.add_row(self._create_pref_check_button(
                'Use a checkered background for transparent images',
                'checkered bg for transparent images'))

        return page

    def _init_behaviour_tab(self):
        # ----------------------------------------------------------------
        # The "Behaviour" tab.
        # ----------------------------------------------------------------
        page = _PreferencePage(None)

        page.new_section('Manga')

        page.add_row(self._create_pref_check_button(
            'Use western style page flipping in manga mode',
            'manga flip right'))

        page.new_section('Scroll')

        page.add_row(self._create_pref_check_button(
                'Flip pages with mouse wheel',
                'flip with wheel'))

        page.add_row(self._create_pref_check_button(
                'Automatically open the next archive',
                'auto open next archive'))

        page.add_row(self._create_pref_check_button(
                'Automatically open next directory',
                'auto open next directory'))

        page.add_row(Gtk.Label(label='Number of pixels to scroll a page per arrow key press:'),
                     self._create_pref_spinner(
                             'number of pixels to scroll per key event',
                             1, 1, 500, 1, 3, 0))

        page.add_row(Gtk.Label(label='Number of pixels to scroll a page per mouse wheel turn:'),
                     self._create_pref_spinner(
                             'number of pixels to scroll per mouse wheel event',
                             1, 1, 500, 1, 3, 0))

        page.new_section('Double page mode')

        page.add_row(self._create_pref_check_button(
                'Flip two pages in double page mode',
                'double step in double page mode'))

        page.add_row(Gtk.Label(label='Show only one page where appropriate:'),
                     self._create_doublepage_as_one_control())

        page.new_section('Page selection')

        page.add_row(self._create_pref_check_button(
            'Goto the first page when opening previous archive (restart required)',
            'open first page'))

        return page

    def _init_display_tab(self):
        # ----------------------------------------------------------------
        # The "Display" tab.
        # ----------------------------------------------------------------
        page = _PreferencePage(None)

        page.new_section('Fullscreen')

        page.add_row(self._create_pref_check_button(
                'Use fullscreen by default',
                'default fullscreen'))

        page.add_row(self._create_pref_check_button(
                'Hide all toolbars in fullscreen',
                'hide all in fullscreen'))

        page.new_section('Fit to size mode')

        page.add_row(Gtk.Label(label='Fit to width or height:'),
                     self._create_fitmode_control())

        page.add_row(Gtk.Label(label='Fixed size for this mode:'),
                     self._create_pref_spinner(
                             'fit to size px',
                             1, 10, 10000, 10, 50, 0))

        page.new_section('Rotation')

        page.add_row(self._create_pref_check_button(
                'Rotate images according to their metadata',
                'auto rotate from exif'))

        page.new_section('Image quality')

        page.add_row(Gtk.Label(label='Scaling mode'),
                     self._create_scaling_quality_combobox())

        page.new_section('Statusbar')

        page.add_row(Gtk.Label(label='Statusbar spacing:'),
                     self._create_pref_spinner(
                             'statusbar spacing',
                             1, 1, 20, 1, 10, 0))

        page.new_section('Cursor')

        page.add_row(self._create_pref_check_button(
                'Hide cursor after delay',
                'hide cursor'))

        return page

    def _init_dialog_tab(self):
        # ----------------------------------------------------------------
        # The "Display" tab.
        # ----------------------------------------------------------------
        page = _PreferencePage(None)

        page.new_section('Bookmark')

        page.add_row(Gtk.Label(label='Bookmark dialog size (width):'),
                     self._create_pref_spinner(
                             'bookmark width',
                             1, 480, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='Bookmark dialog size (height):'),
                     self._create_pref_spinner(
                             'bookmark height',
                             1, 320, 10000, 10, 10, 0))

        page.new_section('Properties')

        page.add_row(Gtk.Label(label='Properties dialog size (width):'),
                     self._create_pref_spinner(
                             'properties width',
                             1, 480, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='Properties dialog size (height):'),
                     self._create_pref_spinner(
                             'properties height',
                             1, 320, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='Properties thumb size:'),
                     self._create_pref_spinner(
                             'properties thumb size',
                             1, 32, 1024, 1, 10, 0))

        page.new_section('Page Selector')

        page.add_row(Gtk.Label(label='window size (width):'),
                     self._create_pref_spinner(
                             'pageselector width',
                             1, 560, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='window size (height):'),
                     self._create_pref_spinner(
                             'pageselector height',
                             1, 820, 10000, 10, 10, 0))

        page.new_section('Main Window')

        page.add_row(self._create_pref_check_button(
                'Save window size',
                'window save'))

        page.add_row(Gtk.Label(label='window size (width):'),
                     self._create_pref_spinner(
                             'window width',
                             1, 480, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='window size (height):'),
                     self._create_pref_spinner(
                             'window height',
                             1, 320, 10000, 10, 10, 0))

        return page

    def _init_animation_tab(self):
        # ----------------------------------------------------------------
        # The "Animation" tab.
        # ----------------------------------------------------------------
        page = _PreferencePage(None)

        page.new_section('Animated images')

        page.add_row(Gtk.Label(label='Animation mode'),
                     self._create_animation_mode_combobox())

        page.add_row(self._create_pref_check_button(
                'Use animation background (otherwise uses Appearance -> Background)',
                'animation background'))

        page.add_row(self._create_pref_check_button(
                'Enable scale, rotate, flip and enhance operation on animation',
                'animation transform'))

        return page

    def _init_advanced_tab(self):
        # ----------------------------------------------------------------
        # The "Advanced" tab.
        # ----------------------------------------------------------------
        page = _PreferencePage(None)

        page.new_section('File order')

        page.add_row(Gtk.Label(label='Sort files and directories by:'),
                     self._create_sort_by_control())

        page.add_row(Gtk.Label(label='Sort archives by:'),
                     self._create_archive_sort_by_control())

        page.new_section('File detection')

        page.add_row(self._create_pref_check_button(
                'Detect image file(s) by mimetypes',
                'check image mimetype'))

        page.new_section('Moving files')

        page.add_row(Gtk.Label(label='Move file location (must be relative)'),
                     self._create_pref_text_box('move file'))

        page.new_section('Extraction and cache')

        page.add_row(Gtk.Label(label='Maximum number of pages to store in the cache (-1 caches everything):'),
                     self._create_pref_spinner(
                             'max pages to cache',
                             1, -1, 500, 1, 3, 0))

        page.new_section('Magnifying Lens')

        page.add_row(Gtk.Label(label='Magnifying lens size (in pixels):'),
                     self._create_pref_spinner(
                             'lens size',
                             1, 50, 400, 1, 10, 0))

        page.add_row(Gtk.Label(label='Magnification lens factor:'),
                     self._create_pref_spinner(
                             'lens magnification',
                             1, 1.1, 10.0, 0.1, 1.0, 1))

        page.new_section('Threads')

        page.add_row(Gtk.Label(label='Maximum number of thumbnail threads:'),
                     self._create_pref_spinner(
                         'max threads thumbnail',
                         1, 1, constants.MAX_THREADS, 1, 4, 0))

        page.add_row(Gtk.Label(label='Maximum number of concurrent extraction threads:'),
                     self._create_pref_spinner(
                         'max threads extract',
                         1, 1, constants.MAX_THREADS, 1, 4, 0))

        page.add_row(Gtk.Label(label='Maximum number of general threads:'),
                     self._create_pref_spinner(
                         'max threads general',
                         1, 1, constants.MAX_THREADS, 1, 4, 0))

        return page

    def _init_shortcuts_tab(self):
        # ----------------------------------------------------------------
        # The "Shortcuts" tab.
        # ----------------------------------------------------------------
        page = KeybindingEditorWindow(self.__manager)

        return page

    def _tab_page_changed(self, notebook, page_ptr, page_num: int):
        """
        Dynamically switches the "Reset" button's text
        depending on the currently selected tab page
        """

        if notebook.get_nth_page(page_num) == self.shortcuts:
            self.__reset_button.set_label('_Reset keys')
            self.__reset_button.set_sensitive(True)
        else:
            self.__reset_button.set_label('Clear _dialog choices')
            self.__reset_button.set_sensitive(len(prefs['stored dialog choices']) > 0)

    def _response(self, dialog, response):
        if response == Gtk.ResponseType.CLOSE:
            PreferenceDialog.close_dialog()

        elif response == constants.RESPONSE_REVERT_TO_DEFAULT:
            if self.notebook.get_nth_page(self.notebook.get_current_page()) == self.shortcuts:
                # "Shortcuts" page is active, reset all keys to their default value
                self.__manager.clear_all()
                self.__window.get_event_handler().register_key_events()
                self.__manager.save()
                self.shortcuts.refresh_model()
            else:
                # Reset stored choices
                prefs['stored dialog choices'] = {}
                self.__reset_button.set_sensitive(False)

        else:
            # Other responses close the dialog, e.g. clicking the X icon on the dialog.
            PreferenceDialog.close_dialog()

    def _create_doublepage_as_one_control(self):
        """
        Creates the ComboBox control for selecting virtual double page options
        """

        items = (
            ('Never', constants.SHOW_DOUBLE_NEVER),
            ('Only for title pages', constants.SHOW_DOUBLE_AS_ONE_TITLE),
            ('Only for wide images', constants.SHOW_DOUBLE_AS_ONE_WIDE),
            ('Always', constants.SHOW_DOUBLE_AS_ONE_TITLE | constants.SHOW_DOUBLE_AS_ONE_WIDE))

        box = self._create_combobox(items,
                                    prefs['virtual double page for fitting images'],
                                    self._double_page_changed_cb)

        return box

    def _double_page_changed_cb(self, combobox, *args):
        """
        Called when a new option was selected for the virtual double page option
        """

        _iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(_iter):
            value = combobox.get_model().get_value(_iter, 1)
            prefs['virtual double page for fitting images'] = value
            self.__window.draw_image()

    def _create_fitmode_control(self):
        """Combobox for fit to size mode"""
        items = (
            ('Fit to width', constants.ZOOM_MODE_WIDTH),
            ('Fit to height', constants.ZOOM_MODE_HEIGHT))

        box = self._create_combobox(items,
                                    prefs['fit to size mode'],
                                    self._fit_to_size_changed_cb)

        return box

    def _fit_to_size_changed_cb(self, combobox, *args):
        """
        Change to 'Fit to size' pixels
        """

        _iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(_iter):
            value = combobox.get_model().get_value(_iter, 1)

            if prefs['fit to size mode'] != value:
                prefs['fit to size mode'] = value
                self.__window.change_zoom_mode()

    def _create_sort_by_control(self):
        """
        Creates the ComboBox control for selecting file sort by options
        """

        sortkey_items = (
            ('No sorting', constants.SORT_NONE),
            ('File name', constants.SORT_NAME),
            ('File name (locale)', constants.SORT_LOCALE),
            ('File size', constants.SORT_SIZE),
            ('Last modified', constants.SORT_LAST_MODIFIED))

        sortkey_box = self._create_combobox(sortkey_items,
                                            prefs['sort by'],
                                            self._sort_by_changed_cb)

        sortorder_items = (
            ('Ascending', constants.SORT_ASCENDING),
            ('Descending', constants.SORT_DESCENDING))

        sortorder_box = self._create_combobox(sortorder_items,
                                              prefs['sort order'],
                                              self._sort_order_changed_cb)

        box = Gtk.HBox()
        box.pack_start(sortkey_box, True, True, 0)
        box.pack_start(sortorder_box, True, True, 0)

        return box

    def _sort_by_changed_cb(self, combobox, *args):
        """
        Called when a new option was selected for the virtual double page option
        """

        _iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(_iter):
            value = combobox.get_model().get_value(_iter, 1)
            prefs['sort by'] = value

            self.__window.filehandler.refresh_file()

    def _sort_order_changed_cb(self, combobox, *args):
        """
        Called when sort order changes (ascending or descending)
        """

        _iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(_iter):
            value = combobox.get_model().get_value(_iter, 1)
            prefs['sort order'] = value

            self.__window.filehandler.refresh_file()

    def _create_archive_sort_by_control(self):
        """
        Creates the ComboBox control for selecting archive sort by options
        """

        sortkey_items = (
            ('No sorting', constants.SORT_NONE),
            ('Natural order', constants.SORT_NAME),
            ('Literal order', constants.SORT_NAME_LITERAL))

        sortkey_box = self._create_combobox(sortkey_items,
                                            prefs['sort archive by'],
                                            self._sort_archive_by_changed_cb)

        sortorder_items = (
            ('Ascending', constants.SORT_ASCENDING),
            ('Descending', constants.SORT_DESCENDING))

        sortorder_box = self._create_combobox(sortorder_items,
                                              prefs['sort archive order'],
                                              self._sort_archive_order_changed_cb)

        box = Gtk.HBox()
        box.pack_start(sortkey_box, True, True, 0)
        box.pack_start(sortorder_box, True, True, 0)

        return box

    def _sort_archive_by_changed_cb(self, combobox, *args):
        """
        Called when a new option was selected for the virtual double page option
        """

        _iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(_iter):
            value = combobox.get_model().get_value(_iter, 1)
            prefs['sort archive by'] = value

            self.__window.filehandler.refresh_file()

    def _sort_archive_order_changed_cb(self, combobox, *args):
        """
        Called when sort order changes (ascending or descending)
        """

        _iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(_iter):
            value = combobox.get_model().get_value(_iter, 1)
            prefs['sort archive order'] = value

            self.__window.filehandler.refresh_file()

    def _create_scaling_quality_combobox(self):
        """
        Creates combo box for image scaling quality
        """

        items = (
            ('Nearest (very fast)', int(GdkPixbuf.InterpType.NEAREST)),
            ('Tiles (fast)', int(GdkPixbuf.InterpType.TILES)),
            ('Bilinear (normal)', int(GdkPixbuf.InterpType.BILINEAR)),
            ('Hyperbolic (slow)', int(GdkPixbuf.InterpType.HYPER)))

        selection = prefs['scaling quality']

        box = self._create_combobox(items, selection, self._scaling_quality_changed_cb)

        return box

    def _scaling_quality_changed_cb(self, combobox, *args):
        """
        Called whan image scaling quality changes
        """

        _iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(_iter):
            value = combobox.get_model().get_value(_iter, 1)
            last_value = prefs['scaling quality']
            prefs['scaling quality'] = value

            if value != last_value:
                self.__window.draw_image()

    def _create_animation_mode_combobox(self):
        """
        Creates combo box for animation mode
        """

        items = (
            ('Never', constants.ANIMATION_DISABLED),
            ('Normal', constants.ANIMATION_NORMAL),
            ('Once', constants.ANIMATION_ONCE),
            ('Infinity', constants.ANIMATION_INF),
        )

        selection = prefs['animation mode']

        box = self._create_combobox(items, selection, self._animation_mode_changed_cb)

        return box

    def _animation_mode_changed_cb(self, combobox, *args):
        """
        Called whenever animation mode has been changed
        """

        _iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(_iter):
            value = combobox.get_model().get_value(_iter, 1)
            last_value = prefs['animation mode']
            prefs['animation mode'] = value

            if value != last_value:
                self.__window.filehandler.refresh_file()

    @staticmethod
    def _create_combobox(options: tuple, selected_value: int, change_callback):
        """
        Creates a new dropdown combobox and populates it with the items passed in C{options}.

        :param options: List of tuples: (Option display text, option value)
        :param selected_value: One of the values passed in C{options} that will
            be pre-selected when the control is created.
        :param change_callback: Function that will be called when the 'changed' event is triggered.
        :returns: Gtk.ComboBox
        """

        assert options and len(options[0]) == 2, 'Invalid format for options.'

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
            if model.get_value(_iter, 1) == selected_value:
                box.set_active_iter(_iter)
                break
            else:
                _iter = model.iter_next(_iter)

        if change_callback:
            box.connect('changed', change_callback)

        return box

    def _create_pref_check_button(self, label: str, prefkey: str):
        button = Gtk.CheckButton(label=label)
        button.set_active(prefs[prefkey])
        button.connect('toggled', self._check_button_cb, prefkey)
        return button

    def _check_button_cb(self, button, preference: str):
        """
        Callback for all checkbutton-type preferences
        """

        prefs[preference] = button.get_active()

        if preference in ('checkered bg for transparent images',
                          'no double page for wide images', 'auto rotate from exif'):
            self.__window.draw_image()

        elif (preference == 'hide all in fullscreen' and
              self.__window.is_fullscreen):
            self.__window.draw_image()

        elif preference in ('animation background', 'animation transform'):
            self.__window.thumbnailsidebar.toggle_page_numbers_visible()

        elif preference in ('animation background', 'animation transform'):
            self.__window.filehandler.refresh_file()

        elif preference in ('check image mimetype',):
            self.__window.filehandler.refresh_file()

    def _create_pref_spinner(self, prefkey: str, scale: int, lower: int, upper: int,
                             step_incr: int, page_incr: int, digits: int):
        value = prefs[prefkey] / scale
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

        if preference == 'lens magnification':
            prefs[preference] = value
        else:
            prefs[preference] = int(value)

        #  now apply new pref
        if preference == 'thumbnail size':
            self.__window.thumbnailsidebar.resize()
            self.__window.draw_image()
        elif preference == 'max pages to cache':
            self.__window.imagehandler.do_cacheing()
        elif preference == 'fit to size px':
            self.__window.change_zoom_mode()

    @staticmethod
    def _create_pref_text_box(preference: str):
        def save_pref_text_box(text):
            prefs[preference] = text.get_text()

        box = Gtk.Entry()
        box.set_text(prefs[preference])
        box.connect('changed', save_pref_text_box)
        return box


class _PreferenceDialog:
    def __init__(self):
        self.__dialog = None

    def open_dialog(self, event, window):
        """
        Create and display the preference dialog
        """

        # if the dialog window is not created then create the window
        if self.__dialog is None:
            self.__dialog = _PreferencesDialog(window)
        else:
            # if the dialog window already exists bring it to the forefront of the screen
            self.__dialog.present()

    def close_dialog(self):
        # if the dialog window exists then destroy it
        if self.__dialog is not None:
            self.__dialog.destroy()
            self.__dialog = None


# Singleton instance
PreferenceDialog = _PreferenceDialog()


class _PreferenceSection(Gtk.VBox):
    """
    The _PreferenceSection is a convenience class for making one
    "section" of a preference-style dialog, e.g. it has a bold header
    and a number of rows which are indented with respect to that header
    """

    def __init__(self, header, right_column_width):
        """
        Contruct a new section with the header set to the text in
        <header>, and the width request of the (possible) right columns
        set to that of <right_column_width>
        """

        super().__init__(homogeneous=False, spacing=0)

        self.__right_column_width = right_column_width
        self.__contentbox = Gtk.VBox(homogeneous=False, spacing=6)
        label = BoldLabel(header)
        label.set_alignment(0, 0.5)
        hbox = Gtk.HBox(homogeneous=False, spacing=0)
        hbox.pack_start(Gtk.HBox(homogeneous=True, spacing=0), False, False, 6)
        hbox.pack_start(self.__contentbox, True, True, 0)
        self.pack_start(label, False, False, 0)
        self.pack_start(hbox, False, False, 6)

    def new_split_vboxes(self):
        """
        Return two new VBoxes that are automatically put in the section
        after the previously added items. The right one has a width request
        equal to the right_column_width value passed to the class contructor,
        in order to make it easy for  all "right column items" in a page to
        line up nicely
        """

        left_box = Gtk.VBox(homogeneous=False, spacing=6)
        right_box = Gtk.VBox(homogeneous=False, spacing=6)

        if self.__right_column_width is not None:
            right_box.set_size_request(self.__right_column_width, -1)

        hbox = Gtk.HBox(homogeneous=False, spacing=12)
        hbox.pack_start(left_box, True, True, 0)
        hbox.pack_start(right_box, False, False, 0)
        self.__contentbox.pack_start(hbox, True, True, 0)
        return left_box, right_box

    def get_contentbox(self):
        return self.__contentbox


class _PreferencePage(Gtk.VBox):
    """
    The _PreferencePage is a conveniece class for making one "page"
    in a preferences-style dialog that contains one or more _PreferenceSections
    """

    def __init__(self, right_column_width):
        """
        Create a new page where any possible right columns have the width request <right_column_width>
        """

        super().__init__(homogeneous=False, spacing=12)
        self.set_border_width(12)
        self.__right_column_width = right_column_width
        self.__section = None

    def new_section(self, header):
        """
        Start a new section in the page, with the header text from <header>
        """

        self.__section = _PreferenceSection(header, self.__right_column_width)
        self.pack_start(self.__section, False, False, 0)

    def add_row(self, left_item, right_item=None):
        """
        Add a row to the page (in the latest section), containing one
        or two items. If the left item is a label it is automatically
        aligned properly
        """

        if isinstance(left_item, Gtk.Label):
            left_item.set_alignment(0, 0.5)

        if right_item is None:
            self.__section.get_contentbox().pack_start(left_item, True, True, 0)
        else:
            left_box, right_box = self.__section.new_split_vboxes()
            left_box.pack_start(left_item, True, True, 0)
            right_box.pack_start(right_item, True, True, 0)
