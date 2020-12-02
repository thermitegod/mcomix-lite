"""main.py - Main window"""

import operator
import shutil
from pathlib import Path

from gi.repository import GLib, Gdk, Gtk
from send2trash import send2trash

from mcomix.bookmark_backend import BookmarksStore
from mcomix.constants import Constants
from mcomix.cursor_handler import CursorHandler
from mcomix.enhance_backend import ImageEnhancer
from mcomix.event import EventHandler
from mcomix.file_handler import FileHandler
from mcomix.icons import Icons
from mcomix.image_handler import ImageHandler
from mcomix.image_tools import ImageTools
from mcomix.keybindings import KeybindingManager
from mcomix.layout import FiniteLayout
from mcomix.lens import MagnifyingLens
from mcomix.lib.callback import Callback
from mcomix.message_dialog import MessageDialog
from mcomix.pageselect import Pageselector
from mcomix.preferences import config
from mcomix.preferences_manager import PreferenceManager
from mcomix.statusbar import Statusbar
from mcomix.thumbbar import ThumbnailSidebar
from mcomix.ui import MainUI
from mcomix.zoom import ZoomModel


class MainWindow(Gtk.Window):
    """
    The main window, is created at start and terminates the program when closed
    """

    def __init__(self, fullscreen: bool = False, manga_mode: bool = False, double_page: bool = False,
                 zoom_mode: int = None, open_path: list = None):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)

        # ----------------------------------------------------------------
        # Attributes
        # ----------------------------------------------------------------
        # Used to detect window fullscreen state transitions.
        self.was_fullscreen = False
        self.is_manga_mode = config['DEFAULT_MANGA_MODE']
        self.__page_orientation = self.page_orientation()
        self.previous_size = (None, None)
        #: Used to remember if changing to fullscreen enabled 'HIDE_ALL'
        self.__hide_all_forced = False
        # Remember last scroll destination.
        self.__last_scroll_destination = Constants.SCROLL_TO['START']

        self.__dummy_layout = FiniteLayout(((1, 1),), (1, 1), (1, 1), 0, False, 0, 0)
        self.__layout = self.__dummy_layout
        self.__spacing = 2
        self.__waiting_for_redraw = False

        self.__main_layout = Gtk.Layout()
        # Wrap main layout into an event box so
        # we  can change its background color.
        self.__event_box = Gtk.EventBox()
        self.__event_box.add(self.__main_layout)
        self.__event_handler = EventHandler(self)
        self.__vadjust = self.__main_layout.get_vadjustment()
        self.__hadjust = self.__main_layout.get_hadjustment()
        self.__scroll = (
            Gtk.Scrollbar.new(Gtk.Orientation.HORIZONTAL, self.__hadjust),
            Gtk.Scrollbar.new(Gtk.Orientation.VERTICAL, self.__vadjust),
        )

        self.filehandler = FileHandler(self)
        self.filehandler.file_closed += self._on_file_closed
        self.filehandler.file_opened += self._on_file_opened
        self.imagehandler = ImageHandler(self)
        self.imagehandler.page_available += self._page_available
        self.thumbnailsidebar = ThumbnailSidebar(self)

        self.statusbar = Statusbar()
        self.cursor_handler = CursorHandler(self)
        self.enhancer = ImageEnhancer(self)
        self.lens = MagnifyingLens(self)
        self.zoom = ZoomModel()
        self.uimanager = MainUI(self)
        self.menubar = self.uimanager.get_widget('/Menu')
        self.popup = self.uimanager.get_widget('/Popup')
        self.actiongroup = self.uimanager.get_action_groups()[0]

        self.images = [Gtk.Image(), Gtk.Image()]  # XXX limited to at most 2 pages

        # ----------------------------------------------------------------
        # Setup
        # ----------------------------------------------------------------
        self.set_title(Constants.APPNAME)
        self.restore_window_geometry()

        # Hook up keyboard shortcuts
        self.__event_handler.register_key_events()

        for img in self.images:
            self.__main_layout.put(img, 0, 0)

        table = Gtk.Table(n_rows=2, n_columns=2, homogeneous=False)
        table.attach(self.thumbnailsidebar, 0, 1, 2, 5, Gtk.AttachOptions.FILL,
                     Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, 0, 0)

        table.attach(self.__event_box, 1, 2, 2, 3, Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND,
                     Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, 0, 0)
        table.attach(self.__scroll[Constants.AXIS['HEIGHT']], 2, 3, 2, 3,
                     Gtk.AttachOptions.FILL | Gtk.AttachOptions.SHRINK,
                     Gtk.AttachOptions.FILL | Gtk.AttachOptions.SHRINK, 0, 0)
        table.attach(self.__scroll[Constants.AXIS['WIDTH']], 1, 2, 4, 5, Gtk.AttachOptions.FILL | Gtk.AttachOptions.SHRINK,
                     Gtk.AttachOptions.FILL, 0, 0)
        table.attach(self.menubar, 0, 3, 0, 1, Gtk.AttachOptions.FILL | Gtk.AttachOptions.SHRINK,
                     Gtk.AttachOptions.FILL, 0, 0)
        table.attach(self.statusbar, 0, 3, 5, 6, Gtk.AttachOptions.FILL | Gtk.AttachOptions.SHRINK,
                     Gtk.AttachOptions.FILL, 0, 0)

        if config['DEFAULT_DOUBLE_PAGE'] or double_page:
            self.actiongroup.get_action('double_page').activate()

        if config['DEFAULT_MANGA_MODE'] or manga_mode:
            self.actiongroup.get_action('manga_mode').activate()

        # Determine zoom mode. If zoom_mode is passed, it overrides
        # the zoom mode preference.
        zoom_actions = {Constants.ZOOM['BEST']: 'best_fit_mode',
                        Constants.ZOOM['WIDTH']: 'fit_width_mode',
                        Constants.ZOOM['HEIGHT']: 'fit_height_mode',
                        Constants.ZOOM['SIZE']: 'fit_size_mode',
                        Constants.ZOOM['MANUAL']: 'fit_manual_mode'}

        if zoom_mode is not None:
            zoom_action = zoom_actions[zoom_mode]
        else:
            zoom_action = zoom_actions[config['ZOOM_MODE']]

        self.actiongroup.get_action(zoom_action).activate()

        if config['STRETCH']:
            self.actiongroup.get_action('stretch').activate()

        if config['KEEP_TRANSFORMATION']:
            config['KEEP_TRANSFORMATION'] = False
            self.actiongroup.get_action('keep_transformation').activate()
        else:
            config['ROTATION'] = 0
            config['VERTICAL_FLIP'] = False
            config['HORIZONTAL_FLIP'] = False

        # List of "toggles" than can be shown/hidden by the user.
        self.__toggle_list = (
            # Preference        Action        Widget(s)
            ('SHOW_MENUBAR', 'menubar', (self.menubar,)),
            ('SHOW_SCROLLBAR', 'scrollbar', self.__scroll),
            ('SHOW_STATUSBAR', 'statusbar', (self.statusbar,)),
            ('SHOW_THUMBNAILS', 'thumbnails', (self.thumbnailsidebar,)),
        )

        # Each "toggle" widget "eats" part of the main layout visible area.
        self.__toggle_axis = {
            self.thumbnailsidebar: Constants.AXIS['WIDTH'],
            self.__scroll[Constants.AXIS['HEIGHT']]: Constants.AXIS['WIDTH'],
            self.__scroll[Constants.AXIS['WIDTH']]: Constants.AXIS['HEIGHT'],
            self.statusbar: Constants.AXIS['HEIGHT'],
            self.menubar: Constants.AXIS['HEIGHT'],
        }

        self.actiongroup.get_action('menu_autorotate_width').set_sensitive(False)
        self.actiongroup.get_action('menu_autorotate_height').set_sensitive(False)

        self.add(table)
        table.show()
        self.__event_box.show_all()

        self.__main_layout.set_events(Gdk.EventMask.BUTTON1_MOTION_MASK |
                                      Gdk.EventMask.BUTTON2_MOTION_MASK |
                                      Gdk.EventMask.BUTTON_PRESS_MASK |
                                      Gdk.EventMask.BUTTON_RELEASE_MASK |
                                      Gdk.EventMask.POINTER_MOTION_MASK)

        self.__main_layout.drag_dest_set(Gtk.DestDefaults.ALL,
                                         [Gtk.TargetEntry.new('text/uri-list', 0, 0)],
                                         Gdk.DragAction.COPY |
                                         Gdk.DragAction.MOVE)

        self.connect('delete_event', self.terminate_program)
        self.connect('key_press_event', self.__event_handler.key_press_event)
        self.connect('configure_event', self.__event_handler.resize_event)
        self.connect('window-state-event', self.__event_handler.window_state_event)

        self.__main_layout.connect('button_release_event', self.__event_handler.mouse_release_event)
        self.__main_layout.connect('scroll_event', self.__event_handler.scroll_wheel_event)
        self.__main_layout.connect('button_press_event', self.__event_handler.mouse_press_event)
        self.__main_layout.connect('motion_notify_event', self.__event_handler.mouse_move_event)
        self.__main_layout.connect('drag_data_received', self.__event_handler.drag_n_drop_event)

        self.show()

        if config['DEFAULT_FULLSCREEN'] or fullscreen:
            toggleaction = self.actiongroup.get_action('fullscreen')
            toggleaction.set_active(True)

        if open_path is not None:
            self.filehandler.open_file(open_path)

        if config['HIDE_CURSOR']:
            self.cursor_handler.auto_hide_on()

            # Make sure we receive *all* mouse motion events,
            # even if a modal dialog is being shown.
            def _on_event(event):
                if Gdk.EventType.MOTION_NOTIFY == event.type:
                    self.cursor_handler.refresh()
                Gtk.main_do_event(event)

            Gdk.event_handler_set(_on_event)

    def get_layout(self):
        return self.__layout

    def get_main_layout(self):
        return self.__main_layout

    def get_hadjust(self):
        return self.__hadjust

    def get_vadjust(self):
        return self.__vadjust

    def get_event_handler(self):
        return self.__event_handler

    def page_orientation(self):
        if self.is_manga_mode:
            return Constants.ORIENTATION['MANGA']
        else:
            return Constants.ORIENTATION['WESTERN']

    def draw_image(self, scroll_to=None):
        """
        Draw the current pages and update the titlebar and statusbar
        """

        # FIXME: what if scroll_to is different?
        if not self.__waiting_for_redraw:  # Don't stack up redraws.
            self.__waiting_for_redraw = True
            GLib.idle_add(self._draw_image, scroll_to, priority=GLib.PRIORITY_HIGH_IDLE)

    def _update_toggle_preference(self, preference: str, toggleaction):
        """
        Update "toggle" widget corresponding <preference>.

        Note: the widget visibily itself is left unchanged
        """

        config[preference] = toggleaction.get_active()
        if preference == 'HIDE_ALL':
            self.update_toggles_sensitivity()
        # Since the size of the drawing area is dependent
        # on the visible "toggles", redraw the page.
        self.draw_image()

    def _should_toggle_be_visible(self, preference: str):
        """
        Return <True> if "toggle" widget for <preference> should be visible
        """

        if self.is_fullscreen():
            visible = not config['HIDE_ALL_IN_FULLSCREEN'] and not config['HIDE_ALL']
        else:
            visible = not config['HIDE_ALL']
        visible &= config[preference]
        if preference == 'SHOW_THUMBNAILS':
            visible &= self.filehandler.get_file_loaded()
            visible &= self.imagehandler.get_number_of_pages() > 0
        return visible

    def update_toggles_sensitivity(self):
        """
        Update each "toggle" widget sensitivity
        """

        sensitive = True
        if config['HIDE_ALL'] or (config['HIDE_ALL_IN_FULLSCREEN'] and self.is_fullscreen()):
            sensitive = False
        for preference, action, widget_list in self.__toggle_list:
            self.actiongroup.get_action(action).set_sensitive(sensitive)

    def _update_toggles_visibility(self):
        """
        Update each "toggle" widget visibility
        """

        for preference, action, widget_list in self.__toggle_list:
            should_be_visible = self._should_toggle_be_visible(preference)
            for widget in widget_list:
                # No change in visibility?
                if should_be_visible != widget.get_visible():
                    (widget.show if should_be_visible else widget.hide)()

    def _draw_image(self, scroll_to: int):
        def vector_opposite(a: int):
            return tuple(map(operator.neg, a))

        self._update_toggles_visibility()

        if not self.filehandler.get_file_loaded():
            self._clear_main_area()
            self.__waiting_for_redraw = False
            return

        if not self.imagehandler.page_is_available():
            # Save scroll destination for when the page becomes available.
            self.__last_scroll_destination = scroll_to
            # If the pixbuf for the current page(s) isn't available clear old pixbufs.
            self._clear_main_area()
            self._show_scrollbars([False] * len(self.__scroll))
            self.__waiting_for_redraw = False
            return

        distribution_axis = Constants.AXIS['DISTRIBUTION']
        alignment_axis = Constants.AXIS['ALIGNMENT']
        pixbuf_count = 2 if self.displayed_double() else 1  # XXX limited to at most 2 pages
        pixbuf_list = list(self.imagehandler.get_pixbufs(pixbuf_count))
        do_not_transform = [ImageTools.disable_transform(x) for x in pixbuf_list]
        size_list = [[pixbuf.get_width(), pixbuf.get_height()] for pixbuf in pixbuf_list]

        orientation = self.__page_orientation

        # Rotation handling:
        # - apply Exif rotation on individual images
        # - apply automatic rotation (size based) on whole page
        # - apply manual rotation on whole page
        if config['AUTO_ROTATE_FROM_EXIF']:
            rotation_list = [ImageTools.get_implied_rotation(pixbuf) for pixbuf in pixbuf_list]
        else:
            rotation_list = [0] * len(pixbuf_list)

        virtual_size = [0, 0]
        for i in range(pixbuf_count):
            if rotation_list[i] in (90, 270):
                size_list[i].reverse()
            size = size_list[i]
            virtual_size[distribution_axis] += size[distribution_axis]
            virtual_size[alignment_axis] = max(virtual_size[alignment_axis], size[alignment_axis])
        rotation = (self._get_size_rotation(*virtual_size) + config['ROTATION']) % 360

        if rotation in (90, 270):
            distribution_axis, alignment_axis = alignment_axis, distribution_axis
            orientation = list(orientation)
            orientation.reverse()
            for i in range(pixbuf_count):
                size_list[i].reverse()
        elif rotation in (180, 270):
            orientation = vector_opposite(orientation)

        for i in range(pixbuf_count):
            rotation_list[i] = (rotation_list[i] + rotation) % 360

        if config['VERTICAL_FLIP']:
            orientation = vector_opposite(orientation)
        if config['HORIZONTAL_FLIP']:
            orientation = vector_opposite(orientation)

        viewport_size = ()  # dummy
        expand_area = False
        scrollbar_requests = [False] * len(self.__scroll)
        scaled_sizes = [(0, 0)]
        union_scaled_size = (0, 0)
        # Visible area size is recomputed depending on scrollbar visibility
        while True:
            self._show_scrollbars(scrollbar_requests)
            new_viewport_size = self.get_visible_area_size()
            if new_viewport_size == viewport_size:
                break
            viewport_size = new_viewport_size
            zoom_dummy_size = list(viewport_size)
            dasize = zoom_dummy_size[distribution_axis] - self.__spacing * (pixbuf_count - 1)
            if dasize <= 0:
                dasize = 1
            zoom_dummy_size[distribution_axis] = dasize
            scaled_sizes = self.zoom.get_zoomed_size(size_list, zoom_dummy_size,
                                                     distribution_axis, do_not_transform)

            self.__layout = FiniteLayout(
                scaled_sizes, viewport_size, orientation, self.__spacing,
                expand_area, distribution_axis, alignment_axis)

            union_scaled_size = self.__layout.get_union_box().get_size()

            scrollbar_requests = [(old or new) for old, new in zip(
                scrollbar_requests, map(operator.lt, viewport_size, union_scaled_size))]

            if len(tuple(filter(None, scrollbar_requests))) > 1 and not expand_area:
                expand_area = True
                viewport_size = ()  # start anew

        for i in range(pixbuf_count):
            pixbuf_list[i] = ImageTools.fit_pixbuf_to_rectangle(
                pixbuf_list[i], scaled_sizes[i], rotation_list[i])

        for i in range(pixbuf_count):
            pixbuf_list[i] = ImageTools.trans_pixbuf(
                pixbuf_list[i],
                flip=config['VERTICAL_FLIP'],
                flop=config['HORIZONTAL_FLIP'])
            pixbuf_list[i] = self.enhancer.enhance(pixbuf_list[i])

        for i in range(pixbuf_count):
            ImageTools.set_from_pixbuf(self.images[i], pixbuf_list[i])

        resolutions = [(*size, scaled_size[0] / size[0])
                       for scaled_size, size in zip(scaled_sizes, size_list)]

        if self.is_manga_mode:
            resolutions.reverse()

        self.statusbar.set_resolution(resolutions)
        self.statusbar.update()

        self.__main_layout.get_bin_window().freeze_updates()

        self.__main_layout.set_size(*union_scaled_size)
        content_boxes = self.__layout.get_content_boxes()
        for i in range(pixbuf_count):
            self.__main_layout.move(self.images[i], *content_boxes[i].get_position())

        for i in range(pixbuf_count):
            self.images[i].show()
        for i in range(pixbuf_count, len(self.images)):
            self.images[i].hide()

        # Reset orientation so scrolling behaviour is sane.
        self.__layout.set_orientation(self.__page_orientation)

        if scroll_to is not None:
            if Constants.SCROLL_TO['START'] == scroll_to:
                index = Constants.INDEX['FIRST']
            elif Constants.SCROLL_TO['END'] == scroll_to:
                index = Constants.INDEX['LAST']
            else:
                index = None
            destination = (scroll_to,) * 2
            self.scroll_to_predefined(destination, index)

        self.__main_layout.get_bin_window().thaw_updates()

        self.__waiting_for_redraw = False

    def _update_page_information(self):
        """Updates the window with information that can be gathered
        even when the page pixbuf(s) aren't ready yet"""
        page_number = self.imagehandler.get_current_page()
        if not page_number:
            return
        if self.displayed_double():
            number_of_pages = 2
            filenames = self.imagehandler.get_page_filename(double=True, manga=self.is_manga_mode)
            filesizes = self.imagehandler.get_page_filesize(double=True, manga=self.is_manga_mode)
            filename = ', '.join(filenames)
            filesize = ', '.join(filesizes)
        else:
            number_of_pages = 1
            filename = self.imagehandler.get_page_filename()
            filesize = self.imagehandler.get_page_filesize()
        self.statusbar.set_page_number(page_number, self.imagehandler.get_number_of_pages(), number_of_pages)
        self.statusbar.set_filename(filename)
        if config['STATUSBAR_FULLPATH']:
            self.statusbar.set_root(self.filehandler.get_path_to_base())
        else:
            self.statusbar.set_root(self.filehandler.get_base_filename())
        self.statusbar.set_mode()
        self.statusbar.set_filesize(filesize)
        self.statusbar.set_filesize_archive(self.filehandler.get_path_to_base())
        self.statusbar.update()
        self.update_title()

    @staticmethod
    def _get_size_rotation(width: int, height: int):
        """
        Determines the rotation to be applied. Returns the degree of rotation (0, 90, 180, 270)
        """

        if (height > width and
                config['AUTO_ROTATE_DEPENDING_ON_SIZE'] in
                (Constants.AUTOROTATE['HEIGHT_90'], Constants.AUTOROTATE['HEIGHT_270'])):
            if config['AUTO_ROTATE_DEPENDING_ON_SIZE'] == Constants.AUTOROTATE['HEIGHT_90']:
                return 90
            else:
                return 270
        elif (width > height and
              config['AUTO_ROTATE_DEPENDING_ON_SIZE'] in
              (Constants.AUTOROTATE['WIDTH_90'], Constants.AUTOROTATE['WIDTH_270'])):
            if config['AUTO_ROTATE_DEPENDING_ON_SIZE'] == Constants.AUTOROTATE['WIDTH_90']:
                return 90
            else:
                return 270

        return 0

    def _page_available(self, page: int):
        """
        Called whenever a new page is ready for displaying
        """

        # Refresh display when currently opened page becomes available.
        current_page = self.imagehandler.get_current_page()
        nb_pages = 2 if self.displayed_double() else 1
        if current_page <= page < (current_page + nb_pages):
            self.draw_image(scroll_to=self.__last_scroll_destination)
            self._update_page_information()

        # Use first page as application icon when opening archives.
        if (page == 1
                and self.filehandler.get_archive_type() is not None
                and config['ARCHIVE_THUMBNAIL_AS_ICON']):
            pixbuf = self.imagehandler.get_thumbnail(page=page, size=(48, 48))
            self.set_icon(pixbuf)

    def _on_file_opened(self):
        number, count = self.filehandler.get_file_number()
        self.statusbar.set_file_number(number, count)
        self.statusbar.update()

    def _on_file_closed(self):
        self.clear()
        self.thumbnailsidebar.hide()
        self.thumbnailsidebar.clear()
        self.set_icon_list(Icons.mcomix_icons())

    def new_page(self, at_bottom: bool = False):
        """
        Draw a *new* page correctly (as opposed to redrawing the same image with a new size or whatever)
        """

        if not config['KEEP_TRANSFORMATION']:
            config['ROTATION'] = 0
            config['HORIZONTAL_FLIP'] = False
            config['VERTICAL_FLIP'] = False

        if at_bottom:
            scroll_to = Constants.SCROLL_TO['END']
        else:
            scroll_to = Constants.SCROLL_TO['START']

        self.draw_image(scroll_to=scroll_to)

    @Callback
    def page_changed(self):
        """
        Called on page change
        """

        self.thumbnailsidebar.load_thumbnails()
        self._update_page_information()

    def set_page(self, num: int, at_bottom: bool = False):
        if num == self.imagehandler.get_current_page():
            return
        self.imagehandler.set_page(num)
        self.page_changed()
        self.new_page(at_bottom=at_bottom)

    def next_book(self):
        archive_open = self.filehandler.get_archive_type() is not None
        next_archive_opened = False
        if config['AUTO_OPEN_NEXT_ARCHIVE']:
            next_archive_opened = self.filehandler.open_archive_direction(forward=True)

        # If "Auto open next archive" is disabled, do not go to the next
        # directory if current file was an archive.
        if not next_archive_opened and \
                config['AUTO_OPEN_NEXT_DIRECTORY'] and \
                (not archive_open or config['AUTO_OPEN_NEXT_ARCHIVE']):
            self.filehandler.open_directory_direction(forward=True)

    def previous_book(self):
        archive_open = self.filehandler.get_archive_type() is not None
        previous_archive_opened = False
        if config['AUTO_OPEN_NEXT_ARCHIVE']:
            previous_archive_opened = self.filehandler.open_archive_direction(forward=False)

        # If "Auto open next archive" is disabled, do not go to the previous
        # directory if current file was an archive.
        if not previous_archive_opened and \
                config['AUTO_OPEN_NEXT_DIRECTORY'] and \
                (not archive_open or config['AUTO_OPEN_NEXT_ARCHIVE']):
            self.filehandler.open_directory_direction(forward=False)

    def flip_page(self, number_of_pages: int, single_step: bool = False):
        if not self.filehandler.get_file_loaded():
            return

        current_page = self.imagehandler.get_current_page()
        current_number_of_pages = self.imagehandler.get_number_of_pages()

        new_page = current_page + number_of_pages
        if (abs(number_of_pages) == 1 and
                not single_step and
                config['DEFAULT_DOUBLE_PAGE'] and
                config['DOUBLE_STEP_IN_DOUBLE_PAGE_MODE']):
            if number_of_pages == +1 and not self.imagehandler.get_virtual_double_page():
                new_page += +1
            elif number_of_pages == -1 and not self.imagehandler.get_virtual_double_page(new_page - 1):
                new_page -= 1

        if new_page <= 0:
            # Only switch to previous page when flipping one page before the
            # first one. (Note: check for (page number <= 1) to handle empty
            # archive case).
            if number_of_pages == -1 and current_page <= +1:
                return self.previous_book()
            # Handle empty archive case.
            new_page = min(+1, current_number_of_pages)
        elif new_page > current_number_of_pages:
            if number_of_pages == +1:
                return self.next_book()
            new_page = current_number_of_pages

        if new_page != current_page:
            self.set_page(new_page, at_bottom=(-1 == number_of_pages))

    def first_page(self):
        if self.imagehandler.get_number_of_pages():
            self.set_page(1)

    def last_page(self):
        number_of_pages = self.imagehandler.get_number_of_pages()
        if number_of_pages:
            self.set_page(number_of_pages)

    def page_select(self, *args):
        Pageselector(self)

    def rotate_x(self, rotation: int, *args):
        config['ROTATION'] = (config['ROTATION'] + rotation) % 360
        self.draw_image()

    def flip_horizontally(self, *args):
        config['HORIZONTAL_FLIP'] = not config['HORIZONTAL_FLIP']
        self.draw_image()

    def flip_vertically(self, *args):
        config['VERTICAL_FLIP'] = not config['VERTICAL_FLIP']
        self.draw_image()

    def change_double_page(self, toggleaction):
        config['DEFAULT_DOUBLE_PAGE'] = toggleaction.get_active()
        self._update_page_information()
        self.draw_image()

    def change_manga_mode(self, toggleaction):
        config['DEFAULT_MANGA_MODE'] = toggleaction.get_active()
        self.is_manga_mode = toggleaction.get_active()
        self.__page_orientation = self.page_orientation()
        self._update_page_information()
        self.draw_image()

    def is_fullscreen(self):
        window_state = self.get_window().get_state()
        return (window_state & Gdk.WindowState.FULLSCREEN) != 0

    def change_fullscreen(self, toggleaction):
        # Disable action until transition if complete.
        toggleaction.set_sensitive(False)
        if toggleaction.get_active():
            self.save_window_geometry()
            self.fullscreen()
        else:
            self.unfullscreen()
        # No need to call draw_image explicitely,
        # as we'll be receiving a window state
        # change or resize event.

    def change_zoom_mode(self, radioaction=None, *args):
        if radioaction:
            config['ZOOM_MODE'] = radioaction.get_current_value()
        self.zoom.set_fit_mode(config['ZOOM_MODE'])
        self.zoom.set_scale_up(config['STRETCH'])
        self.zoom.reset_user_zoom()
        self.draw_image()

    def change_autorotation(self, radioaction=None, *args):
        """
        Switches between automatic rotation modes, depending on which
        radiobutton is currently activated
        """

        if radioaction:
            config['AUTO_ROTATE_DEPENDING_ON_SIZE'] = radioaction.get_current_value()
        self.draw_image()

    def change_stretch(self, toggleaction, *args):
        """
        Toggles stretching small images
        """

        config['STRETCH'] = toggleaction.get_active()
        self.zoom.set_scale_up(config['STRETCH'])
        self.draw_image()

    def change_menubar_visibility(self, toggleaction):
        self._update_toggle_preference('SHOW_MENUBAR', toggleaction)

    def change_statusbar_visibility(self, toggleaction):
        self._update_toggle_preference('SHOW_STATUSBAR', toggleaction)

    def change_scrollbar_visibility(self, toggleaction):
        self._update_toggle_preference('SHOW_SCROLLBAR', toggleaction)

    def change_thumbnails_visibility(self, toggleaction):
        self._update_toggle_preference('SHOW_THUMBNAILS', toggleaction)

    def change_hide_all(self, toggleaction):
        self._update_toggle_preference('HIDE_ALL', toggleaction)

    @staticmethod
    def change_keep_transformation(*args):
        config['KEEP_TRANSFORMATION'] = not config['KEEP_TRANSFORMATION']

    def manual_zoom_in(self, *args):
        self.zoom.zoom_in()
        self.draw_image()

    def manual_zoom_out(self, *args):
        self.zoom.zoom_out()
        self.draw_image()

    def manual_zoom_original(self, *args):
        self.zoom.reset_user_zoom()
        self.draw_image()

    def _show_scrollbars(self, request):
        """
        Enables scroll bars depending on requests and preferences
        """

        limit = self._should_toggle_be_visible('SHOW_SCROLLBAR')
        for idx, item in enumerate(self.__scroll):
            if limit and request[idx]:
                self.__scroll[idx].show()
            else:
                self.__scroll[idx].hide()

    def scroll(self, x: int, y: int):
        """
        Scroll <x> px horizontally and <y> px vertically. If <bound> is
        'first' or 'second', we will not scroll out of the first or second
        page respectively (dependent on manga mode). The <bound> argument
        only makes sense in double page mode.

        :returns: True if call resulted in new adjustment values, False otherwise
        """

        old_hadjust = self.__hadjust.get_value()
        old_vadjust = self.__vadjust.get_value()

        visible_width, visible_height = self.get_visible_area_size()

        hadjust_upper = max(0, self.__hadjust.get_upper() - visible_width)
        vadjust_upper = max(0, self.__vadjust.get_upper() - visible_height)
        hadjust_lower = 0

        new_hadjust = old_hadjust + x
        new_vadjust = old_vadjust + y

        new_hadjust = max(hadjust_lower, new_hadjust)
        new_vadjust = max(0, new_vadjust)

        new_hadjust = min(hadjust_upper, new_hadjust)
        new_vadjust = min(vadjust_upper, new_vadjust)

        self.__vadjust.set_value(new_vadjust)
        self.__hadjust.set_value(new_hadjust)
        self.__scroll[0].queue_resize_no_redraw()
        self.__scroll[1].queue_resize_no_redraw()

        return old_vadjust != new_vadjust or old_hadjust != new_hadjust

    def scroll_to_predefined(self, destination: tuple, index: int = None):
        self.__layout.scroll_to_predefined(destination, index)
        viewport_position = self.__layout.get_viewport_box().get_position()
        self.__hadjust.set_value(viewport_position[0])  # 2D only
        self.__vadjust.set_value(viewport_position[1])  # 2D only
        self.__scroll[0].queue_resize_no_redraw()
        self.__scroll[1].queue_resize_no_redraw()

    def clear(self):
        """
        Clear the currently displayed data (i.e. "close" the file)
        """

        self.set_title(Constants.APPNAME)
        self.statusbar.set_message('')
        self.draw_image()

    def _clear_main_area(self):
        for i in self.images:
            i.hide()
            i.clear()

        self._show_scrollbars([False] * len(self.__scroll))
        self.__layout = self.__dummy_layout
        self.__main_layout.set_size(*self.__layout.get_union_box().get_size())

    def displayed_double(self):
        """
        :returns: True if two pages are currently displayed
        """

        return (self.imagehandler.get_current_page() and
                config['DEFAULT_DOUBLE_PAGE'] and
                not self.imagehandler.get_virtual_double_page() and
                self.imagehandler.get_current_page() != self.imagehandler.get_number_of_pages())

    def get_visible_area_size(self):
        """
        :returns: a 2-tuple with the width and height of the visible part of the main layout area
        """
        dimensions = list(self.get_size())
        size = 0

        for preference, action, widget_list in self.__toggle_list:
            for widget in widget_list:
                if widget.get_visible():
                    axis = self.__toggle_axis[widget]
                    requisition = widget.size_request()
                    if Constants.AXIS['WIDTH'] == axis:
                        size = requisition.width
                    elif Constants.AXIS['HEIGHT'] == axis:
                        size = requisition.height
                    dimensions[axis] -= size

        return tuple(dimensions)

    def set_cursor(self, mode):
        """
        Set the cursor on the main layout area to <mode>. You should
        probably use the cursor_handler instead of using this method directly
        """

        self.__main_layout.get_bin_window().set_cursor(mode)

    def update_title(self):
        """
        Set the title acording to current state
        """

        self.set_title(f'[{self.statusbar.get_page_number()}] '
                       f'{self.imagehandler.get_current_filename()} '
                       f'[{self.statusbar.get_mode()}]')

    def extract_page(self, *args):
        """
        Derive some sensible filename (archive name + _ + filename should do) and offer
        the user the choice to save the current page with the selected name
        """

        save_dialog = Gtk.FileChooserDialog(title='Save page as', action=Gtk.FileChooserAction.SAVE)
        save_dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT, Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        save_dialog.set_transient_for(self)
        save_dialog.set_do_overwrite_confirmation(True)
        save_dialog.set_current_name(self.imagehandler.get_page_filename())

        if save_dialog.run() == Gtk.ResponseType.ACCEPT and save_dialog.get_filename():
            shutil.copy(self.imagehandler.get_path_to_page(), save_dialog.get_filename())

        save_dialog.destroy()

    def move_file(self, move_else_delete: bool = True, *args):
        """
        The currently opened file/archive will be moved to prefs['MOVE_FILE']
        or
        The currently opened file/archive will be trashed after showing a confirmation dialog
        """

        current_file = self.imagehandler.get_real_path()

        def file_action(move: bool = True):
            if move:
                Path.rename(current_file, target_file)
            else:
                send2trash(current_file)

        if move_else_delete:
            target_dir = Path() / current_file.parent / config['MOVE_FILE']
            target_file = Path() / target_dir / current_file.name

            if not Path.exists(target_dir):
                target_dir.mkdir()

        else:
            dialog = MessageDialog(
                parent=self,
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE)
            dialog.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_DELETE, Gtk.ResponseType.OK)
            dialog.set_default_response(Gtk.ResponseType.OK)
            dialog.set_should_remember_choice(
                'delete-opend-file',
                (Gtk.ResponseType.OK,))
            dialog.set_text(f'Trash Selected File: "{current_file.name}"?')
            result = dialog.run()
            if result != Gtk.ResponseType.OK:
                return None

        if self.filehandler.get_archive_type() is not None:
            next_opened = self.filehandler.open_archive_direction(forward=True)
            if not next_opened:
                next_opened = self.filehandler.open_archive_direction(forward=False)
            if not next_opened:
                self.filehandler.close_file()

            if Path.is_file(current_file):
                file_action(move_else_delete)
        else:
            if self.imagehandler.get_number_of_pages() > 1:
                # Open the next/previous file
                if self.imagehandler.get_current_page() >= self.imagehandler.get_number_of_pages():
                    self.flip_page(number_of_pages=-1)
                else:
                    self.flip_page(number_of_pages=+1)
                # Move the desired file
                if Path.is_file(current_file):
                    file_action(move_else_delete)

                # Refresh the directory
                self.filehandler.refresh_file()
            else:
                self.filehandler.close_file()
                if Path.is_file(current_file):
                    file_action(move_else_delete)

    def minimize(self, *args):
        """
        Minimizes the MComix window
        """

        self.iconify()

    def get_window_geometry(self):
        return self.get_position() + self.get_size()

    def save_window_geometry(self):
        if config['WINDOW_SAVE']:
            (
                config['WINDOW_X'],
                config['WINDOW_Y'],
                config['WINDOW_WIDTH'],
                config['WINDOW_HEIGHT'],
            ) = self.get_window_geometry()

    def restore_window_geometry(self):
        if self.get_window_geometry() == (config['WINDOW_X'],
                                          config['WINDOW_Y'],
                                          config['WINDOW_WIDTH'],
                                          config['WINDOW_HEIGHT']):
            return False
        self.resize(config['WINDOW_WIDTH'], config['WINDOW_HEIGHT'])
        self.move(config['WINDOW_X'], config['WINDOW_Y'])
        return True

    def terminate_program(self, *args):
        """
        Run clean-up tasks and exit the program
        """

        if not self.is_fullscreen():
            self.save_window_geometry()

        self.hide()

        if Gtk.main_level() > 0:
            Gtk.main_quit()

        if config['HIDE_ALL'] and self.__hide_all_forced and self.fullscreen:
            config['HIDE_ALL'] = False

        # write config file
        PreferenceManager.write_preferences_file()
        KeybindingManager.keybinding_manager(self).write_keybindings_file()
        BookmarksStore.write_bookmarks_file()

        self.filehandler.close_file()
