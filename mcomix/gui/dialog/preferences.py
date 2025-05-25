# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from gi.repository import GObject, Gtk

from mcomix.lib.events import Events, EventType
from mcomix.preferences import config
from mcomix.gui.dialog.preferences_page import PreferencePage

from mcomix_compiled import Animation, DoublePage, FileSortDirection, FileSortType, ZoomModes

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.gui.main_window import MainWindow


class PreferencesDialog(Gtk.Dialog):
    """
    The preferences dialog where most (but not all) settings that are
    saved between sessions are presented to the user
    """

    def __init__(self, window: MainWindow):
        super().__init__(title='Preferences')

        self.__window = window

        self.__events = Events()

        self.set_modal(True)
        self.set_transient_for(window)

        self.__reset_button = self.add_button('Clear _dialog choices', Gtk.ResponseType.REJECT)
        self.__reset_button.set_sensitive(len(config['STORED_DIALOG_CHOICES']) > 0)
        self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.set_resizable(False)
        self.set_default_response(Gtk.ResponseType.CLOSE)

        self.connect('response', self._response)

        notebook = Gtk.Notebook()
        self.vbox.pack_start(notebook, True, True, 0)
        self.set_border_width(2)
        notebook.set_border_width(2)

        notebook.append_page(self._init_appearance_tab(),
                             Gtk.Label(label='Appearance'))

        notebook.append_page(self._init_behaviour_tab(),
                             Gtk.Label(label='Behaviour'))

        notebook.append_page(self._init_display_tab(),
                             Gtk.Label(label='Display'))

        notebook.append_page(self._init_statusbar_tab(),
                             Gtk.Label(label='Statusbar'))

        notebook.append_page(self._init_animation_tab(),
                             Gtk.Label(label='Animation'))

        notebook.append_page(self._init_advanced_tab(),
                             Gtk.Label(label='Advanced'))

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

        page.new_section('Statusbar')

        page.add_row(self._create_pref_check_button(
            'Show full path of current file in statusbar',
            'STATUSBAR_FULLPATH'))

        page.add_row(self._create_pref_check_button(
            'Show page scaling percent',
            'STATUSBAR_SHOW_SCALE'))

        page.new_section('Bookmarks')

        page.add_row(self._create_pref_check_button(
            'Show bookmark path in bookmark menu',
            'BOOKMARK_SHOW_PATH'))

        return page

    def _init_statusbar_tab(self):

        page = PreferencePage()

        page.new_section('Statusbar')

        page.add_row(self._create_pref_check_button(
            'Show page numbers',
            'STATUSBAR_FIELD_PAGE_NUMBERS'))

        page.add_row(self._create_pref_check_button(
            'Show file numbers',
            'STATUSBAR_FIELD_FILE_NUMBERS'))

        page.add_row(self._create_pref_check_button(
            'Show page resolution',
            'STATUSBAR_FIELD_PAGE_RESOLUTION'))

        page.add_row(self._create_pref_check_button(
            'Show archive filename',
            'STATUSBAR_FIELD_ARCHIVE_NAME'))

        page.add_row(self._create_pref_check_button(
            'Show page filename',
            'STATUSBAR_FIELD_PAGE_FILENAME'))

        page.add_row(self._create_pref_check_button(
            'Show page filesize',
            'STATUSBAR_FIELD_PAGE_FILESIZE'))

        page.add_row(self._create_pref_check_button(
            'Show archive filesize',
            'STATUSBAR_FIELD_ARCHIVE_FILESIZE'))

        page.add_row(self._create_pref_check_button(
            'Show current mode',
            'STATUSBAR_FIELD_VIEW_MODE'))

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
            'Enable scale, rotate, and flip operation on animation',
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
                         2, 0, 50, 1, 3, 0))

        page.add_row(Gtk.Label(label='Pages to cache behind the current page:'),
                     self._create_pref_spinner(
                         'PAGE_CACHE_BEHIND',
                         2, 1, 10, 1, 3, 0))

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

    def _response(self, dialog, response):
        match response:
            case Gtk.ResponseType.REJECT:
                # Reset stored choices
                config['STORED_DIALOG_CHOICES'] = {}
                self.__reset_button.set_sensitive(False)

            case _:
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
            ('Best fit', ZoomModes.BEST),
            ('Fit to width', ZoomModes.WIDTH),
            ('Fit to height', ZoomModes.HEIGHT),
            ('Fit to size', ZoomModes.SIZE),
            ('Manual fit', ZoomModes.MANUAL),
        )

        return self._create_combobox(items, 'ZOOM_MODE')

    def _create_combobox_doublepage_as_one(self):
        """
        Creates the ComboBox control for selecting virtual double page options
        """

        items = (
            ('Never', DoublePage.NEVER),
            ('Only for title pages', DoublePage.AS_ONE_TITLE),
            ('Only for wide images', DoublePage.AS_ONE_WIDE),
            ('Always', DoublePage.ALWAYS))

        return self._create_combobox(items, 'VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES')

    def _create_combobox_fitmode(self):
        """Combobox for fit to size mode"""
        items = (
            ('Fit to width', ZoomModes.WIDTH),
            ('Fit to height', ZoomModes.HEIGHT))

        return self._create_combobox(items, 'FIT_TO_SIZE_MODE')

    def _create_combobox_sort_by(self):
        """
        Creates the ComboBox control for selecting file sort by options
        """

        sortkey_items = (
            ('No sorting', FileSortType.NONE),
            ('File name', FileSortType.NAME),
            ('File size', FileSortType.SIZE),
            ('Last modified', FileSortType.LAST_MODIFIED))

        sortkey_box = self._create_combobox(sortkey_items, 'SORT_BY')

        sortorder_items = (
            ('Ascending', FileSortDirection.ASCENDING),
            ('Descending', FileSortDirection.DESCENDING))

        sortorder_box = self._create_combobox(sortorder_items, 'SORT_ORDER')

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(sortkey_box, True, True, 0)
        box.pack_start(sortorder_box, True, True, 0)

        return box

    def _create_combobox_archive_sort_by(self):
        """
        Creates the ComboBox control for selecting archive sort by options
        """

        sortkey_items = (
            ('No sorting', FileSortType.NONE),
            ('Natural order', FileSortType.NAME),
            ('Literal order', FileSortType.NAME_LITERAL))

        sortkey_box = self._create_combobox(sortkey_items, 'SORT_ARCHIVE_BY')

        sortorder_items = (
            ('Ascending', FileSortDirection.ASCENDING),
            ('Descending', FileSortDirection.DESCENDING))

        sortorder_box = self._create_combobox(sortorder_items, 'SORT_ARCHIVE_ORDER')

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(sortkey_box, True, True, 0)
        box.pack_start(sortorder_box, True, True, 0)

        return box

    def _create_combobox_animation_mode(self):
        """
        Creates combo box for animation mode
        """

        items = (
            ('Never', Animation.DISABLED),
            ('Normal', Animation.NORMAL),
        )

        return self._create_combobox(items, 'ANIMATION_MODE')

    def _changed_cb(self, combobox, preference: str):
        """
        Called whenever cb box has been changed
        """

        _iter = combobox.get_active_iter()
        if not combobox.get_model().iter_is_valid(_iter):
            return

        value = combobox.get_model().get_value(_iter, 1)
        last_value = config[preference]
        if value == last_value:
            return

        config[preference] = value

        match preference:
            case ('ANIMATION_MODE' | 'SORT_ARCHIVE_ORDER' | 'SORT_ARCHIVE_BY' | 'SORT_ORDER' | 'SORT_BY'):
                self.__window.file_handler.refresh_file()
            case ('VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES' | 'CHECKERED_BG_SIZE'):
                self.__events.run_events(EventType.DRAW_PAGE)
            case ('FIT_TO_SIZE_MODE' | 'ZOOM_MODE'):
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
            case ('CHECKERED_BG_FOR_TRANSPARENT_IMAGES'):
                self.__events.run_events(EventType.DRAW_PAGE)
            case ('ANIMATION_BACKGROUND' | 'ANIMATION_TRANSFORM'):
                self.__window.thumbnailsidebar.toggle_page_numbers_visible()
                self.__window.file_handler.refresh_file()
            case ('OPEN_FIRST_PAGE'):
                self.__window.file_handler.update_opening_behavior()

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
        config[preference] = int(value)

        match preference:
            case ('THUMBNAIL_SIZE'):
                self.__window.thumbnailsidebar.resize()
                self.__events.run_events(EventType.DRAW_PAGE)
            case ('PAGE_CACHE_FORWARD' | 'PAGE_CACHE_BEHIND'):
                self.__window.image_handler.do_caching()
            case ('FIT_TO_SIZE_PX'):
                self.__window.change_zoom_mode()

    def _create_pref_text_box(self, preference: str):
        def save_pref_text_box(text):
            config[preference] = text.get_text()

        box = Gtk.Entry()
        box.set_text(config[preference])
        box.connect('changed', save_pref_text_box)
        return box
