# -*- coding: utf-8 -*-

"""preferences_dialog.py - Preferences dialog."""

from gi.repository import GObject, Gdk, GdkPixbuf, Gtk

from mcomix import constants, image_tools, keybindings, keybindings_editor, message_dialog, preferences_page
from mcomix.preferences import prefs

_dialog = None


class _PreferencesDialog(Gtk.Dialog):
    """The preferences dialog where most (but not all) settings that are
    saved between sessions are presented to the user.
    """

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
        behaviour = self._init_behaviour_tab()
        notebook.append_page(behaviour, Gtk.Label(label='Behaviour'))
        display = self._init_display_tab()
        notebook.append_page(display, Gtk.Label(label='Display'))
        advanced = self._init_advanced_tab()
        notebook.append_page(advanced, Gtk.Label(label='Advanced'))
        shortcuts = self.shortcuts = self._init_shortcuts_tab()
        notebook.append_page(shortcuts, Gtk.Label(label='Shortcuts'))

        notebook.connect('switch-page', self._tab_page_changed)
        # Update the Reset button's tooltip
        self._tab_page_changed(notebook, None, 0)

        self.show_all()

    def _init_appearance_tab(self):
        # ----------------------------------------------------------------
        # The "Appearance" tab.
        # ----------------------------------------------------------------
        page = preferences_page._PreferencePage(None)

        page.new_section('User interface')

        page.add_row(self._create_pref_check_button('Escape key closes program', 'escape quits',
                                                    ('When active, the ESC key closes the program, instead of only '
                                                     'disabling fullscreen mode.')))

        page.new_section('Background')

        fixed_bg_button, dynamic_bg_button = self._create_binary_pref_radio_buttons('Use this colour as background:',
                                                                                    'color box bg',
                                                                                    'Always use this selected colour as the background colour.',
                                                                                    'Use dynamic background colour',
                                                                                    'smart bg',
                                                                                    'Automatically pick a background colour that fits the viewed image.')
        page.add_row(fixed_bg_button, self._create_color_button('bg colour'))
        page.add_row(dynamic_bg_button)

        page.new_section('Thumbnails')

        thumb_fixed_bg_button, thumb_dynamic_bg_button = self._create_binary_pref_radio_buttons(
            'Use this colour as the thumbnail background:',
            'color box thumb bg', 'Always use this selected colour as the thumbnail background colour.',
            'Use dynamic background colour',
            'smart thumb bg', 'Automatically use the colour that fits the viewed image for the thumbnail background.')
        page.add_row(thumb_fixed_bg_button, self._create_color_button('thumb bg colour'))
        page.add_row(thumb_dynamic_bg_button)

        page.add_row(self._create_pref_check_button('Show page numbers on thumbnails',
                                                    'show page numbers on thumbnails', None))

        page.add_row(self._create_pref_check_button('Use archive thumbnail as application icon',
                                                    'archive thumbnail as icon',
                                                    'By enabling this setting, the first page of a book will be used as application icon instead of the standard icon.'))

        page.add_row(Gtk.Label(label='Thumbnail size (in pixels):'),
                     self._create_pref_spinner('thumbnail size',
                                               1, 20, 500, 1, 10, 0, None))

        page.new_section('Transparency')

        page.add_row(self._create_pref_check_button('Use checkered background for transparent images',
                                                    'checkered bg for transparent images',
                                                    'Use a grey checkered background for transparent images. If this preference is unset, the background is plain white instead.'))

        return page

    def _init_behaviour_tab(self):
        # ----------------------------------------------------------------
        # The "Behaviour" tab.
        # ----------------------------------------------------------------
        page = preferences_page._PreferencePage(None)

        page.new_section('Scroll')

        page.add_row(self._create_pref_check_button('Use smart scrolling',
                                                    'smart scroll',
                                                    ('With this preference set, the space key and mouse wheel '
                                                     'do not only scroll down or up, but also sideways and so '
                                                     'try to follow the natural reading order of the comic book.')))

        page.add_row(self._create_pref_check_button('Flip pages when scrolling off the edges of the page',
                                                    'flip with wheel',
                                                    'Flip pages when scrolling "off the page" with the scroll wheel or with the arrow keys. It takes n consecutive "steps" with the scroll wheel or the arrow keys for the pages to be flipped.'))

        page.add_row(self._create_pref_check_button('Automatically open the next archive',
                                                    'auto open next archive',
                                                    'Automatically open the next archive in the directory when flipping past the last page, or the previous archive when flipping past the first page.'))

        page.add_row(self._create_pref_check_button('Automatically open next directory',
                                                    'auto open next directory',
                                                    'Automatically open the first file in the next sibling directory when flipping past the last page of the last file in a directory, or the previous directory when flipping past the first page of the first file.'))

        page.add_row(Gtk.Label(label='Number of pixels to scroll per arrow key press:'),
                     self._create_pref_spinner('number of pixels to scroll per key event',
                                               1, 1, 500, 1, 3, 0,
                                               'Set the number of pixels to scroll on a page when using the arrow keys.'))

        page.add_row(Gtk.Label(label='Number of pixels to scroll per mouse wheel turn:'),
                     self._create_pref_spinner('number of pixels to scroll per mouse wheel event',
                                               1, 1, 500, 1, 3, 0,
                                               'Set the number of pixels to scroll on a page when using a mouse wheel.'))

        page.add_row(Gtk.Label(label=('Fraction of page to scroll '
                                      'per space key press (in percent):')),
                     self._create_pref_spinner('smart scroll percentage',
                                               0.01, 1, 100, 1, 5, 0,
                                               ('Sets the percentage by which the page '
                                                'will be scrolled down or up when the space key is pressed.')))

        page.add_row(Gtk.Label(label='Number of "steps" to take before flipping the page:'),
                     self._create_pref_spinner('number of key presses before page turn',
                                               1, 1, 100, 1, 3, 0,
                                               'Set the number of "steps" needed to flip to the next or previous page.  Less steps will allow for very fast page turning but you might find yourself accidentally turning pages.'))

        page.new_section('Double page mode')

        page.add_row(self._create_pref_check_button('Flip two pages in double page mode',
                                                    'double step in double page mode',
                                                    'Flip two pages, instead of one, each time we flip pages in double page mode.'))

        page.add_row(Gtk.Label(label='Show only one page where appropriate:'),
                     self._create_doublepage_as_one_control())

        page.new_section('Files')

        page.add_row(self._create_pref_check_button('Automatically open the last viewed file on startup',
                                                    'auto load last file',
                                                    'Automatically open, on startup, the file that was open when MComix was last closed.'))

        page.add_row(Gtk.Label(label='Store information about recently opened files:'),
                     self._create_store_recent_combobox())

        return page

    def _init_display_tab(self):
        # ----------------------------------------------------------------
        # The "Display" tab.
        # ----------------------------------------------------------------
        page = preferences_page._PreferencePage(None)

        page.new_section('Fullscreen')

        page.add_row(self._create_pref_check_button('Use fullscreen by default',
                                                    'default fullscreen', None))

        page.add_row(self._create_pref_check_button('Automatically hide all toolbars in fullscreen',
                                                    'hide all in fullscreen', None))

        page.new_section('Fit to size mode')

        page.add_row(Gtk.Label(label='Fit to width or height:'),
                     self._create_fitmode_control())

        page.add_row(Gtk.Label(label='Fixed size for this mode:'),
                     self._create_pref_spinner('fit to size px',
                                               1, 10, 10000, 10, 50, 0, None))

        page.new_section('Slideshow')

        page.add_row(Gtk.Label(label='Slideshow delay (in seconds):'),
                     self._create_pref_spinner('slideshow delay',
                                               1000.0, 0.01, 3600.0, 0.1, 1, 2, None))

        page.add_row(Gtk.Label(label='Slideshow step (in pixels):'),
                     self._create_pref_spinner('number of pixels to scroll per slideshow event',
                                               1, -500, 500, 1, 1, 0,
                                               'Specify the number of pixels to scroll while in slideshow mode. A positive value will scroll forward, a negative value will scroll backwards, and a value of 0 will cause the slideshow to always flip to a new page.'))

        page.add_row(self._create_pref_check_button('During a slideshow automatically open the next archive',
                                                    'slideshow can go to next archive',
                                                    'While in slideshow mode allow the next archive to automatically be opened.'))

        page.new_section('Rotation')

        page.add_row(self._create_pref_check_button('Automatically rotate images according to their metadata',
                                                    'auto rotate from exif',
                                                    'Automatically rotate images when an orientation is specified in the image metadata, such as in an Exif tag.'))

        page.new_section('Image quality')

        page.add_row(Gtk.Label(label='Scaling mode'),
                     self._create_scaling_quality_combobox())

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

        page.new_section('Extraction and cache')

        page.add_row(Gtk.Label(label='Maximum number of concurrent extraction threads:'),
                     self._create_pref_spinner('max extract threads',
                                               1, 1, 16, 1, 4, 0,
                                               'Set the maximum number of concurrent threads for formats that support it.'))

        page.add_row(self._create_pref_check_button('Store thumbnails for opened files',
                                                    'create thumbnails',
                                                    'Store thumbnails for opened files according to the freedesktop.org specification. These thumbnails are shared by many other applications, such as most file managers.'))

        page.add_row(Gtk.Label(label='Temporary directory (restart required)'),
                     self._create_pref_folder_chooser('temporary directory', default=None)
                     )

        page.add_row(Gtk.Label(label='Maximum number of pages to store in the cache:'),
                     self._create_pref_spinner('max pages to cache',
                                               1, -1, 500, 1, 3, 0,
                                               'Set the max number of pages to cache. A value of -1 will cache the entire archive.'))

        page.new_section('Magnifying Lens')

        page.add_row(Gtk.Label(label='Magnifying lens size (in pixels):'),
                     self._create_pref_spinner('lens size',
                                               1, 50, 400, 1, 10, 0,
                                               'Set the size of the magnifying lens. It is a square with a side of this many pixels.'))

        page.add_row(Gtk.Label(label='Magnification factor:'),
                     self._create_pref_spinner('lens magnification',
                                               1, 1.1, 10.0, 0.1, 1.0, 1,
                                               'Set the magnification factor of the magnifying lens.'))

        page.new_section('Comments')

        page.add_row(Gtk.Label(label='Comment extensions:'),
                     self._create_extensions_entry())

        page.new_section('Animated images')

        page.add_row(Gtk.Label(label='Animation mode:'),
                     self._create_animation_mode_combobox())

        return page

    def _init_shortcuts_tab(self):
        # ----------------------------------------------------------------
        # The "Shortcuts" tab.
        # ----------------------------------------------------------------
        km = keybindings.keybinding_manager(self._window)
        page = keybindings_editor.KeybindingEditorWindow(km)
        return page

    def _tab_page_changed(self, notebook, page_ptr, page_num):
        """ Dynamically switches the "Reset" button's text and tooltip
        depending on the currently selected tab page. """
        new_page = notebook.get_nth_page(page_num)
        if new_page == self.shortcuts:
            self.reset_button.set_label("_Reset keys")
            self.reset_button.set_tooltip_text("Resets all keyboard shortcuts to their default values.")
            self.reset_button.set_sensitive(True)
        else:
            self.reset_button.set_label('Clear _dialog choices')
            self.reset_button.set_tooltip_text(
                'Clears all dialog choices that you have previously chosen not to be asked again.')
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

    def _language_changed_cb(self, combobox, *args):
        """ Called whenever the language was changed. """
        model_index = combobox.get_active()
        if model_index > -1:
            iter = combobox.get_model().iter_nth_child(None, model_index)
            text, lang_code = combobox.get_model().get(iter, 0, 1)
            prefs['language'] = lang_code

    def _create_doublepage_as_one_control(self):
        """ Creates the ComboBox control for selecting virtual double page options. """
        items = (
            ('Never', 0),
            ('Only for title pages', constants.SHOW_DOUBLE_AS_ONE_TITLE),
            ('Only for wide images', constants.SHOW_DOUBLE_AS_ONE_WIDE),
            ('Always', constants.SHOW_DOUBLE_AS_ONE_TITLE | constants.SHOW_DOUBLE_AS_ONE_WIDE))

        box = self._create_combobox(items,
                                    prefs['virtual double page for fitting images'],
                                    self._double_page_changed_cb)

        box.set_tooltip_text(
            ("When showing the first page of an archive, or an image's width "
             "exceeds its height, only a single page will be displayed."))

        return box

    def _double_page_changed_cb(self, combobox, *args):
        """ Called when a new option was selected for the virtual double page option. """
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            prefs['virtual double page for fitting images'] = value
            self._window.draw_image()

    def _create_fitmode_control(self):
        """ Combobox for fit to size mode """
        items = (
            ('Fit to width', constants.ZOOM_MODE_WIDTH),
            ('Fit to height', constants.ZOOM_MODE_HEIGHT))

        box = self._create_combobox(items,
                                    prefs['fit to size mode'],
                                    self._fit_to_size_changed_cb)

        return box

    def _fit_to_size_changed_cb(self, combobox, *args):
        """ Change to 'Fit to size' pixels """
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)

            if prefs['fit to size mode'] != value:
                prefs['fit to size mode'] = value
                self._window.change_zoom_mode()

    def _create_sort_by_control(self):
        """ Creates the ComboBox control for selecting file sort by options. """
        sortkey_items = (
            ('No sorting', 0),
            ('File name', constants.SORT_NAME),
            ('File size', constants.SORT_SIZE),
            ('Last modified', constants.SORT_LAST_MODIFIED))

        sortkey_box = self._create_combobox(sortkey_items, prefs['sort by'],
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

        label = ("Files will be opened and displayed according to the sort order "
                 "specified here. This option does not affect ordering within archives.")
        sortkey_box.set_tooltip_text(label)
        sortorder_box.set_tooltip_text(label)

        return box

    def _sort_by_changed_cb(self, combobox, *args):
        """ Called when a new option was selected for the virtual double page option. """
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            prefs['sort by'] = value

            self._window.filehandler.refresh_file()

    def _sort_order_changed_cb(self, combobox, *args):
        """ Called when sort order changes (ascending or descending) """
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            prefs['sort order'] = value

            self._window.filehandler.refresh_file()

    def _create_archive_sort_by_control(self):
        """ Creates the ComboBox control for selecting archive sort by options. """
        sortkey_items = (
            ('No sorting', 0),
            ('Natural order', constants.SORT_NAME),
            ('Literal order', constants.SORT_NAME_LITERAL))

        sortkey_box = self._create_combobox(sortkey_items, prefs['sort archive by'],
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

        label = ("Files within archives will be sorted according to the order specified here. "
                 "Natural order will sort numbered files based on their natural order, "
                 "i.e. 1, 2, ..., 10, while literal order uses standard C sorting, "
                 "i.e. 1, 2, 34, 5.")
        sortkey_box.set_tooltip_text(label)
        sortorder_box.set_tooltip_text(label)

        return box

    def _sort_archive_by_changed_cb(self, combobox, *args):
        """ Called when a new option was selected for the virtual double page option. """
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            prefs['sort archive by'] = value

            self._window.filehandler.refresh_file()

    def _sort_archive_order_changed_cb(self, combobox, *args):
        """ Called when sort order changes (ascending or descending) """
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            prefs['sort archive order'] = value

            self._window.filehandler.refresh_file()

    def _create_store_recent_combobox(self):
        """ Creates the combobox for "Store recently opened files". """
        items = (
            ('Never', False),
            ('Always', True))

        # Map legacy 0/1/2 values:
        if prefs['store recent file info'] == 0:
            selection = False
        elif prefs['store recent file info'] in (1, 2):
            selection = True
        else:
            selection = prefs['store recent file info']

        box = self._create_combobox(items, selection, self._store_recent_changed_cb)
        box.set_tooltip_text(
            'Add information about all files opened from within MComix to the shared recent files list.')
        return box

    def _store_recent_changed_cb(self, combobox, *args):
        """ Called when option "Store recently opened files" was changed. """
        iter = combobox.get_active_iter()
        if not combobox.get_model().iter_is_valid(iter):
            return

        value = combobox.get_model().get_value(iter, 1)
        last_value = prefs['store recent file info']
        prefs['store recent file info'] = value
        self._window.filehandler.last_read_page.set_enabled(value)

        # If "Never" was selected, ask to purge recent files.
        if (bool(last_value) is True and value is False
                and (self._window.uimanager.recent.count() > 0
                     or self._window.filehandler.last_read_page.count() > 0)):
            dialog = message_dialog.MessageDialog(self, Gtk.DialogFlags.MODAL,
                                                  Gtk.MessageType.INFO, Gtk.ButtonsType.YES_NO)
            dialog.set_default_response(Gtk.ResponseType.YES)
            dialog.set_text('Delete information about recently opened files?',
                            ('This will remove all entries from the "Recent" menu,'
                             ' and clear information about last read pages.'))
            response = dialog.run()

            if response == Gtk.ResponseType.YES:
                self._window.uimanager.recent.remove_all()
                self._window.filehandler.last_read_page.clear_all()

    def _create_scaling_quality_combobox(self):
        """ Creates combo box for image scaling quality """
        items = (
            ('Normal (fast)', int(GdkPixbuf.InterpType.TILES)),
            ('Bilinear', int(GdkPixbuf.InterpType.BILINEAR)),
            ('Hyperbolic (slow)', int(GdkPixbuf.InterpType.HYPER)))

        selection = prefs['scaling quality']

        box = self._create_combobox(items, selection, self._scaling_quality_changed_cb)
        box.set_tooltip_text(
            'Changes how images are scaled. Slower algorithms result in higher quality resizing, but longer page loading times.')

        return box

    def _scaling_quality_changed_cb(self, combobox, *args):
        """ Called whan image scaling quality changes. """
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            last_value = prefs['scaling quality']
            prefs['scaling quality'] = value

            if value != last_value:
                self._window.draw_image()

    def _create_animation_mode_combobox(self):
        """ Creates combo box for animation mode """
        items = (
            ('Never', constants.ANIMATION_DISABLED),
            ('Normal', constants.ANIMATION_NORMAL))

        selection = prefs['animation mode']

        box = self._create_combobox(items, selection, self._animation_mode_changed_cb)
        box.set_tooltip_text('Controls how animated images should be displayed.')

        return box

    def _animation_mode_changed_cb(self, combobox, *args):
        """ Called whenever animation mode has been changed. """
        iter = combobox.get_active_iter()
        if combobox.get_model().iter_is_valid(iter):
            value = combobox.get_model().get_value(iter, 1)
            last_value = prefs['animation mode']
            prefs['animation mode'] = value

            if value != last_value:
                self._window.filehandler.refresh_file()

    def _create_combobox(self, options, selected_value, change_callback):
        """ Creates a new dropdown combobox and populates it with the items
        passed in C{options}.

        @param options: List of tuples: (Option display text, option value)
        @param selected_value: One of the values passed in C{options} that will
            be pre-selected when the control is created.
        @param change_callback: Function that will be called when the 'changed'
            event is triggered.
        @returns Gtk.ComboBox
        """
        assert options and len(options[0]) == 2, "Invalid format for options."

        # Use the first list item to determine typing of model fields.
        # First field is textual description, second field is value.
        model = Gtk.ListStore(GObject.TYPE_STRING, type(options[0][1]))
        for text, value in options:
            model.append((text, value))

        box = Gtk.ComboBox(model=model)
        renderer = Gtk.CellRendererText()
        box.pack_start(renderer, True)
        box.add_attribute(renderer, "text", 0)

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

    def _create_extensions_entry(self):
        entry = Gtk.Entry()
        entry.set_size_request(200, -1)
        entry.set_text(', '.join(prefs['comment extensions']))
        entry.connect('activate', self._entry_cb)
        entry.connect('focus_out_event', self._entry_cb)
        entry.set_tooltip_text(
            'Treat all files found within archives, that have one of these file endings, as comments.')
        return entry

    def _create_pref_check_button(self, label, prefkey, tooltip_text):
        button = Gtk.CheckButton(label=label)
        button.set_active(prefs[prefkey])
        button.connect('toggled', self._check_button_cb, prefkey)
        if tooltip_text:
            button.set_tooltip_text(tooltip_text)
        return button

    def _create_binary_pref_radio_buttons(self, label1, prefkey1, tooltip_text1,
                                          label2, prefkey2, tooltip_text2):
        button1 = Gtk.RadioButton(label=label1)
        button1.connect('toggled', self._check_button_cb, prefkey1)
        if tooltip_text1:
            button1.set_tooltip_text(tooltip_text1)
        button2 = Gtk.RadioButton(group=button1, label=label2)
        button2.connect('toggled', self._check_button_cb, prefkey2)
        if tooltip_text2:
            button2.set_tooltip_text(tooltip_text2)
        button2.set_active(prefs[prefkey2])
        return button1, button2

    def _create_color_button(self, prefkey):
        rgba = image_tools.color_to_floats_rgba(prefs[prefkey])
        button = Gtk.ColorButton.new_with_rgba(Gdk.RGBA(*rgba))
        button.connect('color_set', self._color_button_cb, prefkey)
        return button

    def _check_button_cb(self, button, preference):
        """Callback for all checkbutton-type preferences."""

        prefs[preference] = button.get_active()

        if preference == 'color box bg' and button.get_active():
            if not prefs['smart bg'] or not self._window.filehandler.file_loaded:
                self._window.set_bg_colour(prefs['bg colour'])

        elif preference == 'smart bg' and button.get_active():
            # if the color is no longer using the smart background then return it to the chosen color
            if not prefs[preference]:
                self._window.set_bg_colour(prefs['bg colour'])
            else:
                # draw_image() will set the main background to the smart background
                self._window.draw_image()

        elif preference == 'color box thumb bg' and button.get_active():
            if prefs[preference]:
                prefs['smart thumb bg'] = False
                prefs['thumbnail bg uses main colour'] = False

                self._window.thumbnailsidebar.change_thumbnail_background_color(prefs['thumb bg colour'])
            else:
                self._window.draw_image()

        elif preference == 'smart thumb bg' and button.get_active():
            if prefs[preference]:
                prefs['color box thumb bg'] = False
                prefs['thumbnail bg uses main colour'] = False

                pixbuf = image_tools.static_image(image_tools.unwrap_image(
                    self._window.images[0]))  # XXX transitional(double page limitation)
                if pixbuf:
                    bg_color = image_tools.get_most_common_edge_colour(pixbuf)
                    self._window.thumbnailsidebar.change_thumbnail_background_color(bg_color)
            else:
                self._window.draw_image()

        elif preference in ('checkered bg for transparent images',
        'no double page for wide images', 'auto rotate from exif'):
            self._window.draw_image()

        elif (preference == 'hide all in fullscreen' and
              self._window.is_fullscreen):
            self._window.draw_image()

        elif preference == 'show page numbers on thumbnails':
            self._window.thumbnailsidebar.toggle_page_numbers_visible()

    def _color_button_cb(self, colorbutton, preference):
        """Callback for the background colour selection button."""

        colour = colorbutton.get_color()

        if preference == 'bg colour':
            prefs['bg colour'] = colour.red, colour.green, colour.blue

            if not prefs['smart bg'] or not self._window.filehandler.file_loaded:
                self._window.set_bg_colour(prefs['bg colour'])

        elif preference == 'thumb bg colour':
            prefs['thumb bg colour'] = colour.red, colour.green, colour.blue

            if not prefs['smart thumb bg'] or not self._window.filehandler.file_loaded:
                self._window.thumbnailsidebar.change_thumbnail_background_color(prefs['thumb bg colour'])

    def _create_pref_spinner(self, prefkey, scale, lower, upper, step_incr,
                             page_incr, digits, tooltip_text):
        value = prefs[prefkey] / scale
        adjustment = Gtk.Adjustment(value=value, lower=lower, upper=upper, step_increment=step_incr,
                                    page_increment=page_incr)
        spinner = Gtk.SpinButton.new(adjustment, 0.0, digits)
        spinner.set_size_request(80, -1)
        spinner.connect('value_changed', self._spinner_cb, prefkey)
        if tooltip_text:
            spinner.set_tooltip_text(tooltip_text)
        return spinner

    def _spinner_cb(self, spinbutton, preference):
        """Callback for spinner-type preferences."""
        value = spinbutton.get_value()

        if preference == 'lens size':
            prefs[preference] = int(value)

        elif preference == 'lens magnification':
            prefs[preference] = value

        elif preference == 'slideshow delay':
            prefs[preference] = int(round(value * 1000))
            self._window.slideshow.update_delay()

        elif preference == 'number of pixels to scroll per slideshow event':
            prefs[preference] = int(value)

        elif preference == 'number of pixels to scroll per key event':
            prefs[preference] = int(value)

        elif preference == 'number of pixels to scroll per mouse wheel event':
            prefs[preference] = int(value)

        elif preference == 'smart scroll percentage':
            prefs[preference] = value / 100.0

        elif preference == 'thumbnail size':
            prefs[preference] = int(value)
            self._window.thumbnailsidebar.resize()
            self._window.draw_image()

        elif preference == 'max pages to cache':
            prefs[preference] = int(value)
            self._window.imagehandler.do_cacheing()

        elif preference == 'number of key presses before page turn':
            prefs['number of key presses before page turn'] = int(value)
            self._window._event_handler._extra_scroll_events = 0

        elif preference == 'fit to size px':
            prefs[preference] = int(value)
            self._window.change_zoom_mode()

        elif preference == 'max extract threads':
            prefs[preference] = int(value)

    def _entry_cb(self, entry, event=None):
        """Callback for entry-type preferences."""
        text = entry.get_text()
        extensions = [e.strip() for e in text.split(',')]
        prefs['comment extensions'] = [e for e in extensions if e]
        self._window.filehandler.update_comment_extensions()

    def _create_pref_folder_chooser(self, preference, default=None):
        ''' Select folder as preference value '''
        box = Gtk.Box()

        chooser = Gtk.Button()
        chooser.set_label(prefs[preference] or default or '(default)')
        chooser.connect('clicked', self._chooser_folder_cb, chooser, preference, default, False)
        reset = Gtk.Button(label='reset')
        reset.connect('clicked', self._chooser_folder_cb, chooser, preference, default, True)
        box.add(chooser)
        box.add(reset)

        return box

    def _chooser_folder_cb(self, widget, chooser, preference, default, is_reset):
        ''' Callback for folder chooser '''
        if is_reset:
            prefs[preference] = default
            chooser.set_label(prefs[preference] or '(default)')
            return
        dialog = Gtk.FileChooserDialog(
            title='Please choose a folder',
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.set_transient_for(self)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL, 'Select',
            Gtk.ResponseType.OK
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            prefs[preference] = dialog.get_filename()
            chooser.set_label(prefs[preference])
        dialog.destroy()


def open_dialog(action, window):
    """Create and display the preference dialog."""

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
