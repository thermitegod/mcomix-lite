"""main.py - Main window"""

import shutil
from pathlib import Path

from gi.repository import GLib, Gdk, Gtk
from loguru import logger
from send2trash import send2trash

from mcomix.bookmark_backend import BookmarkBackend
from mcomix.constants import Constants
from mcomix.cursor_handler import CursorHandler
from mcomix.dialog.dialog_about import DialogAbout
from mcomix.dialog.dialog_enhance import DialogEnhance
from mcomix.dialog.dialog_file_chooser import DialogFileChooser
from mcomix.dialog.dialog_preferences import DialogPreference
from mcomix.dialog.dialog_properties import DialogProperties
from mcomix.enhance_backend import ImageEnhancer
from mcomix.event_handler import EventHandler
from mcomix.file_handler import FileHandler
from mcomix.image_handler import ImageHandler
from mcomix.image_tools import ImageTools
from mcomix.keybindings_manager import KeybindingManager
from mcomix.keybindings_map import KeyBindingsMap
from mcomix.layout import FiniteLayout
from mcomix.lens import MagnifyingLens
from mcomix.lib.callback import Callback
from mcomix.menubar import Menubar
from mcomix.message_dialog import MessageDialog
from mcomix.message_dialog_info import MessageDialogInfo
from mcomix.pageselect import Pageselector
from mcomix.preferences import config
from mcomix.preferences_manager import PreferenceManager
from mcomix.statusbar import Statusbar
from mcomix.thumbnail_sidebar import ThumbnailSidebar
from mcomix.zoom import ZoomModel


class MainWindow(Gtk.ApplicationWindow):
    """
    The main window, is created at start and terminates the program when closed
    """

    def __init__(self, open_path: list = None):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)

        # ----------------------------------------------------------------
        # Attributes
        # ----------------------------------------------------------------

        # Load configuration.
        self.__preference_manager = PreferenceManager()
        self.__preference_manager.load_config_file()

        # Used to detect window fullscreen state transitions.
        self.was_fullscreen = False
        self.is_manga_mode = config['DEFAULT_MANGA_MODE']
        self.__page_orientation = self.page_orientation()
        self.previous_size = (None, None)
        self.displayed_double = False

        # Remember last scroll destination.
        self.__last_scroll_destination = Constants.SCROLL_TO['START']

        self.__dummy_layout = FiniteLayout([(1, 1)], (1, 1), [1, 1], 0, 0)
        self.__layout = self.__dummy_layout
        self.__waiting_for_redraw = False

        self.__main_layout = Gtk.Layout()
        self.__main_scrolled_window = Gtk.ScrolledWindow()

        self.__main_scrolled_window.add(self.__main_layout)

        self.event_handler = EventHandler(self)
        self.__vadjust = self.__main_scrolled_window.get_vadjustment()
        self.__hadjust = self.__main_scrolled_window.get_hadjustment()

        self.filehandler = FileHandler(self)
        self.filehandler.file_closed += self._on_file_closed
        self.filehandler.file_opened += self._on_file_opened
        self.imagehandler = ImageHandler(self)
        self.imagehandler.page_available += self._page_available

        self.bookmark_backend = BookmarkBackend(self)

        self.thumbnailsidebar = ThumbnailSidebar(self)
        self.thumbnailsidebar.hide()

        self.statusbar = Statusbar()
        self.cursor_handler = CursorHandler(self)
        self.enhancer = ImageEnhancer(self)
        self.lens = MagnifyingLens(self)
        self.zoom = ZoomModel()

        self.menubar = Menubar(self)

        self.keybindings_map = KeyBindingsMap(self).BINDINGS
        self.keybindings = KeybindingManager(self)

        self.images = [Gtk.Image(), Gtk.Image()]  # XXX limited to at most 2 pages

        # ----------------------------------------------------------------
        # Setup
        # ----------------------------------------------------------------
        self.set_title(Constants.APPNAME)
        self.restore_window_geometry()

        # Hook up keyboard shortcuts
        self.event_handler.event_handler_init()
        self.event_handler.register_key_events()

        for img in self.images:
            self.__main_layout.put(img, 0, 0)

        grid = Gtk.Grid()
        grid.attach(self.menubar, 0, 0, 2, 1)
        grid.attach(self.thumbnailsidebar, 0, 1, 1, 1)
        grid.attach_next_to(self.__main_scrolled_window, self.thumbnailsidebar, Gtk.PositionType.RIGHT, 1, 1)
        self.__main_scrolled_window.set_hexpand(True)
        self.__main_scrolled_window.set_vexpand(True)
        grid.attach(self.statusbar, 0, 2, 2, 1)
        self.add(grid)

        self.change_zoom_mode()

        if not config['KEEP_TRANSFORMATION']:
            config['ROTATION'] = 0

        # Each widget "eats" part of the main layout visible area.
        self.__toggle_axis = {
            self.thumbnailsidebar: Constants.AXIS['WIDTH'],
            self.statusbar: Constants.AXIS['HEIGHT'],
            self.menubar: Constants.AXIS['HEIGHT'],
        }

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
        self.connect('key_press_event', self.event_handler.key_press_event)
        self.connect('configure_event', self.event_handler.resize_event)
        self.connect('window-state-event', self.event_handler.window_state_event)

        self.__main_layout.connect('button_release_event', self.event_handler.mouse_release_event)
        self.__main_layout.connect('scroll_event', self.event_handler.scroll_wheel_event)
        self.__main_layout.connect('button_press_event', self.event_handler.mouse_press_event)
        self.__main_layout.connect('motion_notify_event', self.event_handler.mouse_move_event)
        self.__main_layout.connect('drag_data_received', self.event_handler.drag_n_drop_event)

        self.show_all()

        if open_path:
            self.filehandler.initialize_fileprovider(path=open_path)
            self.filehandler.open_file(Path(open_path[0]))

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
        return self.event_handler

    def page_orientation(self):
        if self.is_manga_mode:
            return Constants.ORIENTATION['MANGA']
        else:
            return Constants.ORIENTATION['WESTERN']

    def draw_image(self, scroll_to=None):
        """
        Draw the current pages and update the titlebar and statusbar
        """

        if self.__waiting_for_redraw:
            # Don't stack up redraws.
            return

        self.__waiting_for_redraw = True
        GLib.idle_add(self._draw_image, scroll_to, priority=GLib.PRIORITY_HIGH_IDLE)

    def _draw_image(self, scroll_to: int):
        if not self.filehandler.get_file_loaded():
            self.thumbnailsidebar.hide()
            self._clear_main_area()
            self.__waiting_for_redraw = False
            return

        self.thumbnailsidebar.show()

        if not self.imagehandler.page_is_available():
            # Save scroll destination for when the page becomes available.
            self.__last_scroll_destination = scroll_to
            # If the pixbuf for the current page(s) isn't available clear old pixbufs.
            self._clear_main_area()
            self.__waiting_for_redraw = False
            return

        distribution_axis = Constants.AXIS['DISTRIBUTION']
        alignment_axis = Constants.AXIS['ALIGNMENT']
        # XXX limited to at most 2 pages
        pixbuf_count = 2 if self.displayed_double else 1
        pixbuf_count_iter = range(pixbuf_count)
        pixbuf_list = list(self.imagehandler.get_pixbufs(pixbuf_count))
        do_not_transform = [ImageTools.disable_transform(x) for x in pixbuf_list]
        size_list = [[pixbuf.get_width(), pixbuf.get_height()] for pixbuf in pixbuf_list]

        # Rotation handling:
        # - apply Exif rotation on individual images
        # - apply automatic rotation (size based) on whole page
        # - apply manual rotation on whole page
        if config['AUTO_ROTATE_FROM_EXIF']:
            rotation_list = [ImageTools.get_implied_rotation(pixbuf) for pixbuf in pixbuf_list]
        else:
            rotation_list = [0] * len(pixbuf_list)

        virtual_size = [0, 0]
        for i in pixbuf_count_iter:
            if rotation_list[i] in (90, 270):
                size_list[i].reverse()
            size = size_list[i]
            virtual_size[distribution_axis] += size[distribution_axis]
            virtual_size[alignment_axis] = max(virtual_size[alignment_axis], size[alignment_axis])
        rotation = (self._get_size_rotation(*virtual_size) + config['ROTATION']) % 360

        orientation = self.__page_orientation
        if rotation in (90, 270):
            distribution_axis, alignment_axis = alignment_axis, distribution_axis
            orientation.reverse()
            for i in pixbuf_count_iter:
                size_list[i].reverse()
        elif rotation in (180, 270):
            orientation.reverse()

        # Recompute the visible area size
        viewport_size = self.get_visible_area_size()
        zoom_dummy_size = list(viewport_size)
        scaled_sizes = self.zoom.get_zoomed_size(size_list, zoom_dummy_size, distribution_axis, do_not_transform)

        self.__layout = FiniteLayout(scaled_sizes, viewport_size, orientation, distribution_axis, alignment_axis)

        for i in pixbuf_count_iter:
            rotation_list[i] = (rotation_list[i] + rotation) % 360

            pixbuf_list[i] = ImageTools.fit_pixbuf_to_rectangle(pixbuf_list[i], scaled_sizes[i], rotation_list[i])
            pixbuf_list[i] = self.enhancer.enhance(pixbuf_list[i])

            ImageTools.set_from_pixbuf(self.images[i], pixbuf_list[i])

        resolutions = [(*size, scaled_size[0] / size[0])
                       for scaled_size, size in zip(scaled_sizes, size_list)]

        if self.is_manga_mode:
            resolutions.reverse()
        self.statusbar.set_resolution(resolutions)
        self.statusbar.update()

        self.__main_layout.get_bin_window().freeze_updates()

        self.__main_layout.set_size(*self.__layout.get_union_box().get_size())

        for i in self.images:
            # hides old images before showing new ones
            # also if in double page mode and only a single
            # image is going to be shown, prevents a ghost second image
            i.hide()

        content_boxes = self.__layout.get_content_boxes()
        for i in pixbuf_count_iter:
            self.__main_layout.move(self.images[i], *content_boxes[i].get_position())
            self.images[i].show()

        # Reset orientation so scrolling behaviour is sane.
        self.__layout.set_orientation(self.__page_orientation)

        if scroll_to is not None:
            destination = (scroll_to,) * 2
            self.scroll_to_predefined(destination)

        self.__main_layout.get_bin_window().thaw_updates()

        self.__waiting_for_redraw = False

    def _update_page_information(self):
        """
        Updates the window with information that can be gathered
        even when the page pixbuf(s) aren't ready yet
        """

        page = self.imagehandler.get_current_page()
        if not page:
            return

        if self.displayed_double:
            number_of_pages = 2
            filenames = self.imagehandler.get_page_filename(page=page, double_mode=True, manga=self.is_manga_mode)
            filesizes = self.imagehandler.get_page_filesize(page=page, double_mode=True, manga=self.is_manga_mode)
        else:
            number_of_pages = 1
            filenames = self.imagehandler.get_page_filename(page=page)
            filesizes = self.imagehandler.get_page_filesize(page=page)

        filename = ', '.join(filenames)
        filesize = ', '.join(filesizes)

        self.statusbar.set_page_number(page, self.imagehandler.get_number_of_pages(), number_of_pages)
        self.statusbar.set_filename(filename)
        self.statusbar.set_filesize(filesize)

        self.statusbar.update()

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

    def _get_virtual_double_page(self, page: int = None):
        """
        Return True if the current state warrants use of virtual
        double page mode (i.e. if double page mode is on, the corresponding
        preference is set, and one of the two images that should normally
        be displayed has a width that exceeds its height), or if currently
        on the first page

        :returns: True if the current state warrants use of virtual double page mode
        """

        if page is None:
            page = self.imagehandler.get_current_page()

        if (page == 1 and
                config['VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES'] & Constants.DOUBLE_PAGE['AS_ONE_TITLE'] and
                self.filehandler.get_archive_type() is not None):
            return True

        if (not config['DEFAULT_DOUBLE_PAGE'] or
                not config['VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES'] & Constants.DOUBLE_PAGE['AS_ONE_WIDE'] or
                self.imagehandler.is_last_page(page)):
            return False

        for page in (page, page + 1):
            if not self.imagehandler.page_is_available(page):
                return False
            pixbuf = self.imagehandler.get_pixbuf(page - 1)
            width, height = pixbuf.get_width(), pixbuf.get_height()
            if config['AUTO_ROTATE_FROM_EXIF']:
                rotation = ImageTools.get_implied_rotation(pixbuf)

                # if rotation not in (0, 90, 180, 270):
                #     return

                if rotation in (90, 270):
                    width, height = height, width
            if width > height:
                return True

        return False

    def _page_available(self, page: int):
        """
        Called whenever a new page is ready for displaying
        """

        # Refresh display when currently opened page becomes available.
        current_page = self.imagehandler.get_current_page()
        nb_pages = 2 if self.displayed_double else 1
        if current_page <= page < (current_page + nb_pages):
            self._displayed_double()
            self.draw_image(scroll_to=self.__last_scroll_destination)
            self._update_page_information()

    def _on_file_opened(self):
        self._displayed_double()
        self.thumbnailsidebar.show()

        if config['STATUSBAR_FULLPATH']:
            self.statusbar.set_archive_filename(self.filehandler.get_path_to_base())
        else:
            self.statusbar.set_archive_filename(self.filehandler.get_base_filename())
        self.statusbar.set_view_mode()
        self.statusbar.set_filesize_archive(self.filehandler.get_path_to_base())
        self.statusbar.set_file_number(*self.filehandler.get_file_number())
        self.statusbar.update()

        self._update_title()

    def _on_file_closed(self):
        self.clear()
        self.thumbnailsidebar.hide()
        self.thumbnailsidebar.clear()

    def new_page(self, at_bottom: bool = False):
        """
        Draw a *new* page correctly (as opposed to redrawing the same image with a new size or whatever)
        """

        if not config['KEEP_TRANSFORMATION']:
            config['ROTATION'] = 0

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

        self._displayed_double()
        self.thumbnailsidebar.hide()
        self.thumbnailsidebar.load_thumbnails()
        self._update_page_information()

    def set_page(self, num: int, at_bottom: bool = False):
        if num == self.imagehandler.get_current_page():
            return
        self.imagehandler.set_page(num)
        self.page_changed()
        self.new_page(at_bottom=at_bottom)

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
            if number_of_pages == +1 and not self._get_virtual_double_page():
                new_page += +1
            elif number_of_pages == -1 and not self._get_virtual_double_page(new_page - 1):
                new_page -= 1

        if new_page <= 0:
            # Only switch to previous page when flipping one page before the
            # first one. (Note: check for (page number <= 1) to handle empty
            # archive case).
            if number_of_pages == -1 and current_page <= +1:
                return self.filehandler.open_archive_direction(forward=False)
            # Handle empty archive case.
            new_page = min(+1, current_number_of_pages)
        elif new_page > current_number_of_pages:
            if number_of_pages == +1:
                return self.filehandler.open_archive_direction(forward=True)
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

    def rotate_90(self, *args):
        self.rotate_x(rotation=90)

    def rotate_180(self, *args):
        self.rotate_x(rotation=180)

    def rotate_270(self, *args):
        self.rotate_x(rotation=270)

    def rotate_x(self, rotation: int, *args):
        config['ROTATION'] = (config['ROTATION'] + rotation) % 360
        self.draw_image()

    def change_double_page(self, *args):
        config['DEFAULT_DOUBLE_PAGE'] = not config['DEFAULT_DOUBLE_PAGE']
        self._displayed_double()
        self.statusbar.set_view_mode()
        self._update_page_information()
        self.draw_image()

    def change_manga_mode(self, *args):
        config['DEFAULT_MANGA_MODE'] = not config['DEFAULT_MANGA_MODE']
        self.is_manga_mode = config['DEFAULT_MANGA_MODE']
        self.__page_orientation = self.page_orientation()
        self.statusbar.set_view_mode()
        self._update_page_information()
        self.draw_image()

    def is_fullscreen(self):
        window_state = self.get_window().get_state()
        return (window_state & Gdk.WindowState.FULLSCREEN) != 0

    def change_fullscreen(self, *args):
        # Disable action until transition if complete.

        if self.is_fullscreen():
            self.unfullscreen()
        else:
            self.save_window_geometry()
            self.fullscreen()

        # No need to call draw_image explicitely,
        # as we'll be receiving a window state
        # change or resize event.

    def change_fit_mode_best(self, *args):
        self.change_zoom_mode(value=Constants.ZOOM['BEST'])

    def change_fit_mode_width(self, *args):
        self.change_zoom_mode(value=Constants.ZOOM['WIDTH'])

    def change_fit_mode_height(self, *args):
        self.change_zoom_mode(value=Constants.ZOOM['HEIGHT'])

    def change_fit_mode_size(self, *args):
        self.change_zoom_mode(value=Constants.ZOOM['SIZE'])

    def change_fit_mode_manual(self, *args):
        self.change_zoom_mode(value=Constants.ZOOM['MANUAL'])

    def change_zoom_mode(self, value: int = None):
        if value is not None:
            config['ZOOM_MODE'] = value
        self.zoom.set_fit_mode(config['ZOOM_MODE'])
        self.zoom.set_scale_up(config['STRETCH'])
        self.zoom.reset_user_zoom()
        self.draw_image()

    def change_autorotation(self, value=None, *args):
        """
        Switches between automatic rotation modes, depending on which
        radiobutton is currently activated
        """

        if value:
            config['AUTO_ROTATE_DEPENDING_ON_SIZE'] = value
        self.draw_image()

    def toggle_image_scaling(self):
        config['ENABLE_PIL_SCALING'] = not config['ENABLE_PIL_SCALING']
        self.draw_image()
        self.statusbar.update_image_scaling()
        self.statusbar.update()

    def change_image_scaling(self, step: int):
        if config['ENABLE_PIL_SCALING']:
            config_key = 'PIL_SCALING_FILTER'
            algos = Constants.SCALING_PIL
        else:
            config_key = 'GDK_SCALING_FILTER'
            algos = Constants.SCALING_GDK

        # inc/dec active algo, modulus loops algos to start on overflow
        # and end on underflow
        config[config_key] = algos[(config[config_key] + step) % len(algos)].value

        self.draw_image()
        self.statusbar.update_image_scaling()
        self.statusbar.update()

    def change_stretch(self, *args):
        """
        Toggles stretching small images
        """

        config['STRETCH'] = not config['STRETCH']
        self.zoom.set_scale_up(config['STRETCH'])
        self.draw_image()

    def open_dialog_file_chooser(self, *args):
        DialogFileChooser().open_dialog(self)

    def open_dialog_properties(self, *args):
        DialogProperties().open_dialog(self)

    def open_dialog_preference(self, *args):
        DialogPreference().open_dialog(self)

    def open_dialog_enhance(self, *args):
        DialogEnhance().open_dialog(self)

    def open_dialog_about(self, *args):
        DialogAbout().open_dialog(self)

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

        return old_vadjust != new_vadjust or old_hadjust != new_hadjust

    def scroll_to_predefined(self, destination: tuple):
        self.__layout.scroll_to_predefined(destination)
        viewport_position = self.__layout.get_viewport_box().get_position()
        self.__hadjust.set_value(viewport_position[0])  # 2D only
        self.__vadjust.set_value(viewport_position[1])  # 2D only

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

        self.__layout = self.__dummy_layout
        self.__main_layout.set_size(*self.__layout.get_union_box().get_size())

    def _displayed_double(self):
        """
        sets True if two pages are currently displayed
        """

        self.displayed_double = (self.imagehandler.get_current_page() and
                                 config['DEFAULT_DOUBLE_PAGE'] and
                                 not self._get_virtual_double_page() and
                                 not self.imagehandler.is_last_page())

    def get_visible_area_size(self):
        """
        :returns: a 2-tuple with the width and height of the visible part of the main layout area
        """

        dimensions = list(self.get_size())
        size = 0

        for widget, axis in self.__toggle_axis.items():
            minimum_size, natural_size = widget.get_preferred_size()
            if Constants.AXIS['WIDTH'] == axis:
                size = natural_size.width
            elif Constants.AXIS['HEIGHT'] == axis:
                size = natural_size.height
            dimensions[axis] -= size

        return tuple(dimensions)

    def set_cursor(self, mode):
        """
        Set the cursor on the main layout area to <mode>. You should
        probably use the cursor_handler instead of using this method directly
        """

        self.__main_layout.get_bin_window().set_cursor(mode)

    def _update_title(self):
        """
        Set the title acording to current state
        """

        self.set_title(f'{Constants.APPNAME} [{self.imagehandler.get_current_filename()}]')

    def extract_page(self, *args):
        """
        Derive some sensible filename (archive name + _ + filename should do) and offer
        the user the choice to save the current page with the selected name
        """

        page = self.imagehandler.get_current_page()

        if self.displayed_double:
            # asks for left or right page if in double page mode
            # and not showing a single page

            response_left = 70
            response_right = 80

            dialog = MessageDialog(
                parent=self,
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE)
            dialog.add_buttons(
                'Left', response_left,
                'Right', response_right,
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
            dialog.set_default_response(Gtk.ResponseType.CANCEL)
            dialog.set_text(primary='Extract Left or Right page?')
            result = dialog.run()

            if result not in (response_left, response_right):
                return None

            if result == response_left:
                if self.is_manga_mode:
                    page += 1
            elif result == response_right:
                if not self.is_manga_mode:
                    page += 1

        page_name = self.imagehandler.get_page_filename(page=page)[0]
        page_path = self.imagehandler.get_path_to_page(page=page)

        save_dialog = Gtk.FileChooserDialog(title='Save page as', action=Gtk.FileChooserAction.SAVE)
        save_dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT, Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        save_dialog.set_modal(True)
        save_dialog.set_transient_for(self)
        save_dialog.set_do_overwrite_confirmation(True)
        save_dialog.set_current_name(page_name)

        if save_dialog.run() == Gtk.ResponseType.ACCEPT and save_dialog.get_filename():
            shutil.copy(page_path, save_dialog.get_filename())

        save_dialog.destroy()

    def move_file(self, *args):
        """
        The currently opened file/archive will be moved to prefs['MOVE_FILE']
        """

        current_file = self.imagehandler.get_real_path()

        target_dir = Path() / current_file.parent / config['MOVE_FILE']
        target_file = Path() / target_dir / current_file.name

        if not Path.exists(target_dir):
            target_dir.mkdir()

        try:
            self._load_next_file()
        except Exception:
            logger.error(f'File action failed: move_file()')

        if current_file.is_file():
            Path.rename(current_file, target_file)

        if not target_file.is_file():
            MessageDialogInfo(self, primary='File was not moved', secondary=f'{target_file}')

    def trash_file(self, *args):
        """
        The currently opened file/archive will be trashed after showing a confirmation dialog
        """

        current_file = self.imagehandler.get_real_path()

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
        dialog.set_text('Trash Selected File?', secondary=f'{current_file.name}')
        result = dialog.run()
        if result != Gtk.ResponseType.OK:
            return

        try:
            self._load_next_file()
        except Exception:
            logger.error(f'File action failed: trash_file()')

        if current_file.is_file():
            send2trash(bytes(current_file))

        if current_file.is_file():
            MessageDialogInfo(self, primary='File was not deleted', secondary=f'{current_file}')

    def _load_next_file(self):
        """
        Shared logic for move_file() and trash_file()
        """

        if self.filehandler.get_archive_type() is not None:
            next_opened = self.filehandler.open_archive_direction(forward=True)
            if not next_opened:
                next_opened = self.filehandler.open_archive_direction(forward=False)
            if not next_opened:
                self.filehandler.close_file()
        else:
            if self.imagehandler.get_number_of_pages() > 1:
                # Open the next/previous file
                if self.imagehandler.is_last_page():
                    self.flip_page(number_of_pages=-1)
                else:
                    self.flip_page(number_of_pages=+1)

                # Refresh the directory
                self.filehandler.refresh_file()
            else:
                self.filehandler.close_file()

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

        # write config file
        self.__preference_manager.write_config_file()
        self.keybindings.write_keybindings_file()
        self.bookmark_backend.write_bookmarks_file()

        self.filehandler.close_file()
