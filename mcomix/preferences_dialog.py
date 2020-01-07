# -*- coding: utf-8 -*-

"""preferences_dialog.py - Preferences dialog"""

from gi.repository import GObject, Gdk, GdkPixbuf, Gtk

from mcomix import constants, keybindings, keybindings_editor, preferences_page
from mcomix.preferences import prefs

_dialog = None


class _PreferencesDialog(Gtk.Dialog):
    """The preferences dialog where most (but not all) settings that are
    saved between sessions are presented to the user"""

    def __init__(self, window):
        super(_PreferencesDialog, self).__init__(title='Preferences')
        self.set_transient_for(window)

        # Button text is set later depending on active tab
        self.reset_button = self.add_button('', constants.RESPONSE_REVERT_TO_DEFAULT)
        self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self._window = window
        self.set_resizable(True)
        self.set_default_response(Gtk.ResponseType.CLOSE)

        self.connect('response', self._response)

        notebook = self.notebook = Gtk.Notebook()
        self.vbox.pack_start(notebook, True, True, 0)
        self.set_border_width(4)
        notebook.set_border_width(6)

        appearance = self._init_appearance_tab()
        notebook.append_page(appearance, Gtk.Label(label='Appearance'))
        onscrdisp = self._init_onscrdisp_tab()
        notebook.append_page(onscrdisp, Gtk.Label(label='OSD'))
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
        page = preferences_page._PreferencePage(None)

        page.new_section('User interface')

        page.add_row(self._create_pref_check_button(
                'Escape key closes program',
                'escape quits'))

        page.new_section('Background')

        fixed_bg_button = self._create_binary_pref_radio_buttons(
                'Background color',
                'color box bg')
        page.add_row(fixed_bg_button, self._create_color_button('bg color'))

        page.new_section('Thumbnails')

        thumb_fixed_bg_button = self._create_binary_pref_radio_buttons(
                'Thumbnail background color',
                'color box thumb bg')
        page.add_row(thumb_fixed_bg_button, self._create_color_button('thumb bg color'))

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

        page.add_row(Gtk.Label(label='Maximum number of thumbnail threads (0 will use all cores):'),
                     self._create_pref_spinner(
                             'max thumbnail threads',
                             1, 0, constants.CPU_COUNT, 1, 4, 0))

        page.new_section('Transparency')

        page.add_row(self._create_pref_check_button(
                'Use a checkered background for transparent images',
                'checkered bg for transparent images'))

        return page

    def _init_onscrdisp_tab(self):
        # ----------------------------------------------------------------
        # The "OSD" tab.
        # ----------------------------------------------------------------
        page = preferences_page._PreferencePage(None)

        page.new_section('Onscreen display')

        page.add_row(Gtk.Label(label='Timeout (seconds):'),
                     self._create_pref_spinner(
                             'osd timeout',
                             1.0, 0.5, 30.0, 0.5, 2.0, 1))

        page.add_row(Gtk.Label(label='Max font size (8 to 60):'),
                     self._create_pref_spinner(
                             'osd max font size',
                             1, 8, 60, 1, 10, 0))

        page.add_row(Gtk.Label(label='Font color:'),
                     self._create_color_button('osd color'))

        page.add_row(Gtk.Label(label='Background color:'),
                     self._create_color_button('osd bg color'))

        return page

    def _init_behaviour_tab(self):
        # ----------------------------------------------------------------
        # The "Behaviour" tab.
        # ----------------------------------------------------------------
        page = preferences_page._PreferencePage(None)

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

        page.add_row(Gtk.Label(label='Number of "steps" to take before flipping the page (smaller = faster):'),
                     self._create_pref_spinner(
                             'number of key presses before page turn',
                             1, 1, 100, 1, 3, 0))

        page.new_section('Double page mode')

        page.add_row(self._create_pref_check_button(
                'Flip two pages in double page mode',
                'double step in double page mode'))

        page.add_row(Gtk.Label(label='Show only one page where appropriate:'),
                     self._create_doublepage_as_one_control())

        return page

    def _init_display_tab(self):
        # ----------------------------------------------------------------
        # The "Display" tab.
        # ----------------------------------------------------------------
        page = preferences_page._PreferencePage(None)

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
        page = preferences_page._PreferencePage(None)

        page.new_section('Bookmark')

        page.add_row(Gtk.Label(label='Bookmark dialog size (width):'),
                     self._create_pref_spinner(
                             'bookmark width',
                             1, 480, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='Bookmark dialog size (height):'),
                     self._create_pref_spinner(
                             'bookmark height',
                             1, 320, 10000, 10, 10, 0))

        page.new_section('Openwith')

        page.add_row(Gtk.Label(label='Openwith dialog size (width):'),
                     self._create_pref_spinner(
                             'openwith width',
                             1, 480, 10000, 10, 10, 0))

        page.add_row(Gtk.Label(label='Openwith dialog size (height):'),
                     self._create_pref_spinner(
                             'openwith height',
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

        page.new_section('Main window')

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
        page = preferences_page._PreferencePage(None)

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
        page = preferences_page._PreferencePage(None)

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
                     self._create_pref_path_chooser('move file', folder=True, default='keep'))

        page.new_section('Extraction and cache')

        page.add_row(Gtk.Label(label='Maximum number of concurrent extraction threads:'),
                     self._create_pref_spinner(
                             'max extract threads',
                             1, 1, 16, 1, 4, 0))

        page.add_row(self._create_pref_check_button(
                'Store thumbnails for opened files (freedesktop.org compliant)',
                'create thumbnails'))

        page.add_row(Gtk.Label(label='Temporary directory (restart required)'),
                     self._create_pref_path_chooser('temporary directory', folder=True, default='/tmp'))

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

        return page

    def _init_shortcuts_tab(self):
        # ----------------------------------------------------------------
        # The "Shortcuts" tab.
        # ----------------------------------------------------------------
        km = keybindings.keybinding_manager(self._window)
        page = keybindings_editor.KeybindingEditorWindow(km)

        return page

    def _tab_page_changed(self, notebook, page_ptr, page_num):
        """Dynamically switches the "Reset" button's text
        depending on the currently selected tab page"""
        if notebook.get_nth_page(page_num) == self.shortcuts:
            self.reset_button.set_label('_Reset keys')
            self.reset_button.set_sensitive(True)
        else:
            self.reset_button.set_label('Clear _dialog choices')
            self.reset_button.set_sensitive(len(prefs['stored dialog choices']) > 0)

    def _response(self, dialog, response):
        if response == Gtk.ResponseType.CLOSE:
            _close_dialog()

        elif response == constants.RESPONSE_REVERT_TO_DEFAULT:
            if self.notebook.get_nth_page(self.notebook.get_current_page()) == self.shortcuts:
                # "Shortcuts" page is active, reset all keys to their default value
                km = keybindings.keybinding_manager(self._window)
                km.clear_all()
                self._window._event_handler.register_key_events()
                km.save()
                self.shortcuts.refresh_model()
            else:
                # Reset stored choices
                prefs['stored dialog choices'] = {}
                self.reset_button.set_sensitive(False)

        else:
            # Other responses close the dialog, e.g. clicking the X icon on the dialog.
            _close_dialog()

    def _create_doublepage_as_one_control(self):
        """Creates the ComboBox control for selecting virtual double page options"""
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
        """Called when a new option was selected for the virtual double page option"""
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            prefs['virtual double page for fitting images'] = value
            self._window.draw_image()

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
        """Change to 'Fit to size' pixels"""
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)

            if prefs['fit to size mode'] != value:
                prefs['fit to size mode'] = value
                self._window.change_zoom_mode()

    def _create_sort_by_control(self):
        """Creates the ComboBox control for selecting file sort by options"""
        sortkey_items = (
            ('No sorting', constants.SORT_NONE),
            ('File name', constants.SORT_NAME),
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
        """Called when a new option was selected for the virtual double page option"""
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            prefs['sort by'] = value

            self._window.filehandler.refresh_file()

    def _sort_order_changed_cb(self, combobox, *args):
        """Called when sort order changes (ascending or descending)"""
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            prefs['sort order'] = value

            self._window.filehandler.refresh_file()

    def _create_archive_sort_by_control(self):
        """Creates the ComboBox control for selecting archive sort by options"""
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
        """Called when a new option was selected for the virtual double page option"""
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            prefs['sort archive by'] = value

            self._window.filehandler.refresh_file()

    def _sort_archive_order_changed_cb(self, combobox, *args):
        """Called when sort order changes (ascending or descending)"""
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            prefs['sort archive order'] = value

            self._window.filehandler.refresh_file()

    def _create_scaling_quality_combobox(self):
        """Creates combo box for image scaling quality"""
        items = (
            ('Nearest (very fast)', int(GdkPixbuf.InterpType.NEAREST)),
            ('Tiles (fast)', int(GdkPixbuf.InterpType.TILES)),
            ('Bilinear (normal)', int(GdkPixbuf.InterpType.BILINEAR)),
            ('Hyperbolic (slow)', int(GdkPixbuf.InterpType.HYPER)))

        selection = prefs['scaling quality']

        box = self._create_combobox(items, selection, self._scaling_quality_changed_cb)

        return box

    def _scaling_quality_changed_cb(self, combobox, *args):
        """Called whan image scaling quality changes"""
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            last_value = prefs['scaling quality']
            prefs['scaling quality'] = value

            if value != last_value:
                self._window.draw_image()

    def _create_animation_mode_combobox(self):
        """Creates combo box for animation mode"""
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
        """Called whenever animation mode has been changed"""
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            last_value = prefs['animation mode']
            prefs['animation mode'] = value

            if value != last_value:
                self._window.filehandler.refresh_file()

    @staticmethod
    def _create_combobox(options, selected_value, change_callback):
        """Creates a new dropdown combobox and populates it with the items passed in C{options}.
        @param options: List of tuples: (Option display text, option value)
        @param selected_value: One of the values passed in C{options} that will
            be pre-selected when the control is created.
        @param change_callback: Function that will be called when the 'changed' event is triggered.
        @returns Gtk.ComboBox"""
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
        iter = model.get_iter_first()
        while iter:
            if model.get_value(iter, 1) == selected_value:
                box.set_active_iter(iter)
                break
            else:
                iter = model.iter_next(iter)

        if change_callback:
            box.connect('changed', change_callback)

        return box

    def _create_pref_check_button(self, label, prefkey):
        button = Gtk.CheckButton(label=label)
        button.set_active(prefs[prefkey])
        button.connect('toggled', self._check_button_cb, prefkey)
        return button

    def _create_binary_pref_radio_buttons(self, label, prefkey):
        button = Gtk.RadioButton(label=label)
        button.connect('toggled', self._check_button_cb, prefkey)
        return button

    def _create_color_button(self, prefkey):
        rgba = prefs[prefkey]
        button = Gtk.ColorButton.new_with_rgba(Gdk.RGBA(*rgba))
        button.set_use_alpha(True)
        button.connect('color_set', self._color_button_cb, prefkey)
        return button

    def _check_button_cb(self, button, preference):
        """Callback for all checkbutton-type preferences"""
        prefs[preference] = button.get_active()

        if preference == 'color box bg' and button.get_active():
            if not self._window.filehandler.file_loaded:
                self._window.set_bg_color(prefs['bg color'])

        elif preference == 'color box thumb bg' and button.get_active():
            if prefs[preference]:
                prefs['thumbnail bg uses main color'] = False

                self._window.thumbnailsidebar.change_thumbnail_background_color(prefs['thumb bg color'])
            else:
                self._window.draw_image()

        elif preference in ('checkered bg for transparent images',
                            'no double page for wide images', 'auto rotate from exif'):
            self._window.draw_image()

        elif (preference == 'hide all in fullscreen' and
              self._window.is_fullscreen):
            self._window.draw_image()

        elif preference in ('animation background', 'animation transform'):
            self._window.thumbnailsidebar.toggle_page_numbers_visible()

        elif preference in ('animation background', 'animation transform'):
            self._window.filehandler.refresh_file()

        elif preference in ('check image mimetype',):
            self._window.filehandler.refresh_file()

    def _color_button_cb(self, colorbutton, preference):
        """Callback for the background color selection button"""
        color = colorbutton.get_rgba()
        prefs[preference] = color.red, color.green, color.blue, color.alpha

        if preference == 'bg color':
            if not self._window.filehandler.file_loaded:
                self._window.set_bg_color(prefs['bg color'])

        elif preference == 'thumb bg color':
            if not self._window.filehandler.file_loaded:
                self._window.thumbnailsidebar.change_thumbnail_background_color(prefs['thumb bg color'])

    def _create_pref_spinner(self, prefkey, scale, lower, upper, step_incr, page_incr, digits):
        value = prefs[prefkey] / scale
        adjustment = Gtk.Adjustment(value=value, lower=lower, upper=upper, step_increment=step_incr,
                                    page_increment=page_incr)
        spinner = Gtk.SpinButton.new(adjustment, 0.0, digits)
        spinner.set_size_request(80, -1)
        spinner.connect('value_changed', self._spinner_cb, prefkey)
        return spinner

    def _spinner_cb(self, spinbutton, preference):
        """Callback for spinner-type preferences"""
        value = spinbutton.get_value()

        if preference == ('lens magnification' or 'osd timeout'):
            prefs[preference] = value
        else:
            prefs[preference] = int(value)

        #  now apply new pref
        if preference == 'thumbnail size':
            self._window.thumbnailsidebar.resize()
            self._window.draw_image()
        elif preference == 'max pages to cache':
            self._window.imagehandler.do_cacheing()
        elif preference == 'fit to size px':
            self._window.change_zoom_mode()

    def _create_pref_path_chooser(self, preference, folder=False, default=None):
        """Select path as preference value"""
        box = Gtk.Box()
        action = Gtk.FileChooserAction.SELECT_FOLDER if folder else Gtk.FileChooserAction.OPEN

        chooser = Gtk.Button()
        chooser.set_label(prefs[preference] or default or '(default)')
        chooser.connect('clicked', self._path_chooser_cb, chooser, action, preference, default)
        reset = Gtk.Button(label='reset')
        reset.connect('clicked', self._path_chooser_reset_cb, chooser, preference, default)
        box.add(chooser)
        box.add(reset)

        return box

    def _path_chooser_cb(self, widget, chooser, chooser_action, preference, default):
        """Callback for path chooser"""
        dialog = Gtk.FileChooserDialog(title='Please choose a folder', action=chooser_action)
        dialog.set_transient_for(self)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            prefs[preference] = dialog.get_filename()
            chooser.set_label(prefs[preference])
        dialog.destroy()

    @staticmethod
    def _path_chooser_reset_cb(widget, chooser, preference, default):
        """Reset path chooser"""
        prefs[preference] = default
        chooser.set_label(prefs[preference] or '(default)')


def open_dialog(action, window):
    """Create and display the preference dialog"""
    global _dialog

    # if the dialog window is not created then create the window
    if _dialog is None:
        _dialog = _PreferencesDialog(window)
    else:
        # if the dialog window already exists bring it to the forefront of the screen
        _dialog.present()


def _close_dialog():
    global _dialog

    # if the dialog window exists then destroy it
    if _dialog is not None:
        _dialog.destroy()
        _dialog = None
