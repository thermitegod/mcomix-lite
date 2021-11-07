# -*- coding: utf-8 -*-

"""main.py - Main window"""

from pathlib import Path

from gi.repository import GLib, Gdk, Gtk

from mcomix.bookmark_backend import BookmarkBackend
from mcomix.cursor_handler import CursorHandler
from mcomix.dialog_chooser import DialogChooser, DialogChoice
from mcomix.enhance_backend import ImageEnhancer
from mcomix.enums.double_page import DoublePage
from mcomix.enums.mcomix import Mcomix
from mcomix.enums.page_orientation import PageOrientation
from mcomix.enums.image_scaling import ScalingGDK, ScalingPIL
from mcomix.enums.scroll import Scroll
from mcomix.enums.zoom_modes import ZoomAxis, ZoomModes
from mcomix.event_handler import EventHandler
from mcomix.file_handler import FileHandler
from mcomix.filesystem_actions import FileSystemActions
from mcomix.image_handler import ImageHandler
from mcomix.image_tools import ImageTools
from mcomix.keybindings_manager import KeybindingManager
from mcomix.keybindings_map import KeyBindingsMap
from mcomix.layout import FiniteLayout
from mcomix.lens import MagnifyingLens
from mcomix.lib.callback import Callback
from mcomix.menubar import Menubar
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

        # Load configuration.
        self.__preference_manager = PreferenceManager()
        self.__preference_manager.load_config_file()

        # Image display mode
        self.is_manga_mode = config['DEFAULT_MANGA_MODE']
        self.displayed_double = False

        # Used to detect window fullscreen state transitions.
        self.was_fullscreen = False
        self.__page_orientation = self.page_orientation()
        self.previous_size = (None, None)

        # Remember last scroll destination.
        self.__last_scroll_destination = Scroll.START.value

        self.__dummy_layout = FiniteLayout([(1, 1)], (1, 1), [1, 1], 0, 0)
        self.__layout = self.__dummy_layout
        self.__waiting_for_redraw = False

        self.__filehandler = FileHandler(self)
        self.__filehandler.file_closed += self._on_file_closed
        self.__filehandler.file_opened += self._on_file_opened

        self.__filesystem_hactions = FileSystemActions(self)

        self.__imagehandler = ImageHandler(self)
        self.__imagehandler.page_available += self._page_available

        self.__bookmark_backend = BookmarkBackend(self)

        self.__thumbnailsidebar = ThumbnailSidebar(self)
        self.__thumbnailsidebar.hide()

        self.__statusbar = Statusbar()
        self.__enhancer = ImageEnhancer(self)

        self.__zoom = ZoomModel()
        self.__zoom.set_fit_mode(config['ZOOM_MODE'])
        self.__zoom.set_scale_up(config['STRETCH'])
        self.__zoom.reset_user_zoom()

        self.__menubar = Menubar(self)

        self.__event_handler = EventHandler(self)

        self.__keybindings_map = KeyBindingsMap(self).BINDINGS
        self.__keybindings = KeybindingManager(self)

        # Hook up keyboard shortcuts
        self.__event_handler.event_handler_init()
        self.__event_handler.register_key_events()

        self.__cursor_handler = CursorHandler(self)
        self.__lens = MagnifyingLens(self)

        self.__main_layout = Gtk.Layout()
        self.__main_scrolled_window = Gtk.ScrolledWindow()
        self.__main_scrolled_window.add(self.__main_layout)
        self.__main_scrolled_window.set_hexpand(True)
        self.__main_scrolled_window.set_vexpand(True)
        self.__vadjust = self.__main_scrolled_window.get_vadjustment()
        self.__hadjust = self.__main_scrolled_window.get_hadjustment()

        grid = Gtk.Grid()
        grid.attach(self.__menubar, 0, 0, 2, 1)
        grid.attach(self.__thumbnailsidebar, 0, 1, 1, 1)
        grid.attach_next_to(self.__main_scrolled_window, self.__thumbnailsidebar, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach(self.__statusbar, 0, 2, 2, 1)
        self.add(grid)

        # XXX limited to at most 2 pages
        self.images = [Gtk.Image(), Gtk.Image()]
        for img in self.images:
            self.__main_layout.put(img, 0, 0)

        # Each widget "eats" part of the main layout visible area.
        self.__toggle_axis = {
            self.__thumbnailsidebar: ZoomAxis.WIDTH.value,
            self.__statusbar: ZoomAxis.HEIGHT.value,
            self.__menubar: ZoomAxis.HEIGHT.value,
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
        self.connect('key_press_event', self.__event_handler.key_press_event)
        self.connect('configure_event', self.__event_handler.resize_event)
        self.connect('window-state-event', self.__event_handler.window_state_event)

        self.__main_layout.connect('button_release_event', self.__event_handler.mouse_release_event)
        self.__main_layout.connect('scroll_event', self.__event_handler.scroll_wheel_event)
        self.__main_layout.connect('button_press_event', self.__event_handler.mouse_press_event)
        self.__main_layout.connect('motion_notify_event', self.__event_handler.mouse_move_event)
        self.__main_layout.connect('drag_data_received', self.__event_handler.drag_n_drop_event)
        self.__main_layout.connect('motion-notify-event', self.__lens.motion_event)
        self.__main_layout.connect('motion-notify-event', self.__cursor_handler.refresh)

        self.set_title(Mcomix.APP_NAME.value)
        self.restore_window_geometry()

        if config['DEFAULT_FULLSCREEN']:
            self.change_fullscreen()

        self.show_all()

        if open_path:
            self.__filehandler.initialize_fileprovider(path=open_path)
            self.__filehandler.open_file(Path(open_path[0]))

    @property
    def filehandler(self):
        """
        Interface for FileHandler
        """

        return self.__filehandler

    @property
    def imagehandler(self):
        """
        Interface for ImageHandler
        """

        return self.__imagehandler

    @property
    def bookmark_backend(self):
        """
        Interface for BookmarkBackend
        """

        return self.__bookmark_backend

    @property
    def thumbnailsidebar(self):
        """
        Interface for ThumbnailSidebar
        """

        return self.__thumbnailsidebar

    @property
    def statusbar(self):
        """
        Interface for Statusbar
        """

        return self.__statusbar

    @property
    def enhancer(self):
        """
        Interface for ImageEnhancer
        """

        return self.__enhancer

    @property
    def event_handler(self):
        """
        Interface for EventHandler
        """

        return self.__event_handler

    @property
    def keybindings_map(self):
        """
        Interface for KeyBindingsMap
        """

        return self.__keybindings_map

    @property
    def keybindings(self):
        """
        Interface for KeybindingManager
        """

        return self.__keybindings

    @property
    def cursor_handler(self):
        """
        Interface for CursorHandler
        """

        return self.__cursor_handler

    @property
    def lens(self):
        """
        Interface for MagnifyingLens
        """

        return self.__lens

    @property
    def layout(self):
        return self.__layout

    @property
    def main_layout(self):
        return self.__main_layout

    @property
    def hadjust(self):
        return self.__hadjust

    @property
    def vadjust(self):
        return self.__vadjust

    def page_orientation(self):
        if self.is_manga_mode:
            return PageOrientation.MANGA.value
        else:
            return PageOrientation.WESTERN.value

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
        # hides old images before showing new ones
        # also if in double page mode and only a single
        # image is going to be shown, prevents a ghost second image
        for i in self.images:
            i.clear()

        if not self.__filehandler.get_file_loaded():
            self.__thumbnailsidebar.hide()
            self.__waiting_for_redraw = False
            return

        self.__thumbnailsidebar.show()

        if not self.__imagehandler.page_is_available():
            # Save scroll destination for when the page becomes available.
            self.__last_scroll_destination = scroll_to
            self.__waiting_for_redraw = False
            return

        distribution_axis = ZoomAxis.DISTRIBUTION.value
        alignment_axis = ZoomAxis.ALIGNMENT.value
        # XXX limited to at most 2 pages
        pixbuf_count = 2 if self.displayed_double else 1
        pixbuf_count_iter = range(pixbuf_count)
        pixbuf_list = list(self.__imagehandler.get_pixbufs(pixbuf_count))
        do_not_transform = [ImageTools.disable_transform(x) for x in pixbuf_list]
        size_list = [[pixbuf.get_width(), pixbuf.get_height()] for pixbuf in pixbuf_list]

        # Rotation handling:
        # - apply Exif rotation on individual images
        # - apply manual rotation on whole page
        orientation = self.__page_orientation
        if config['AUTO_ROTATE_FROM_EXIF']:
            rotation_list = [ImageTools.get_implied_rotation(pixbuf) for pixbuf in pixbuf_list]
            for i in pixbuf_count_iter:
                if rotation_list[i] in (90, 270):
                    size_list[i].reverse()
        else:
            # no auto rotation
            rotation_list = [0] * len(pixbuf_list)

        rotation = config['ROTATION'] % 360
        match rotation:
            case (90|270):
                distribution_axis, alignment_axis = alignment_axis, distribution_axis
                orientation.reverse()
                for i in pixbuf_count_iter:
                    size_list[i].reverse()
            case 180:
                orientation.reverse()

        # Recompute the visible area size
        viewport_size = self.get_visible_area_size()
        zoom_dummy_size = list(viewport_size)
        scaled_sizes = self.__zoom.get_zoomed_size(size_list, zoom_dummy_size, distribution_axis, do_not_transform)

        self.__layout = FiniteLayout(scaled_sizes, viewport_size, orientation, distribution_axis, alignment_axis)

        content_boxes = self.__layout.get_content_boxes()

        for i in pixbuf_count_iter:
            rotation_list[i] = (rotation_list[i] + rotation) % 360

            pixbuf_list[i] = ImageTools.fit_pixbuf_to_rectangle(pixbuf_list[i], scaled_sizes[i], rotation_list[i])
            pixbuf_list[i] = self.__enhancer.enhance(pixbuf_list[i])

            ImageTools.set_from_pixbuf(self.images[i], pixbuf_list[i])

            self.__main_layout.move(self.images[i], *content_boxes[i].get_position())
            self.images[i].show()

        # Reset orientation so scrolling behaviour is sane.
        self.__layout.set_orientation(self.__page_orientation)

        if scroll_to is not None:
            destination = (scroll_to,) * 2
            self.scroll_to_predefined(destination)

        # update statusbar
        resolutions = [(*size, scaled_size[0] / size[0]) for scaled_size, size in zip(scaled_sizes, size_list, strict=True)]
        if self.is_manga_mode:
            resolutions.reverse()
        self.__statusbar.set_resolution(resolutions)
        self.__statusbar.update()

        self.__waiting_for_redraw = False

    def _update_page_information(self):
        """
        Updates the window with information that can be gathered
        even when the page pixbuf(s) aren't ready yet
        """

        page = self.__imagehandler.get_current_page()
        if not page:
            return

        if self.displayed_double:
            filenames = self.__imagehandler.get_page_filename(page=page, double_mode=True, manga=self.is_manga_mode)
            filesizes = self.__imagehandler.get_page_filesize(page=page, double_mode=True, manga=self.is_manga_mode)
        else:
            filenames = self.__imagehandler.get_page_filename(page=page)
            filesizes = self.__imagehandler.get_page_filesize(page=page)

        filename = ', '.join(filenames)
        filesize = ', '.join(filesizes)

        self.__statusbar.set_page_number(page, self.__imagehandler.get_number_of_pages(),
                                       self.displayed_double, self.is_manga_mode)
        self.__statusbar.set_filename(filename)
        self.__statusbar.set_filesize(filesize)

        self.__statusbar.update()

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
            page = self.__imagehandler.get_current_page()

        if (page == 1 and
                config['VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES'] & DoublePage.AS_ONE_TITLE.value and
                self.__filehandler.is_archive()):
            return True

        if (not config['DEFAULT_DOUBLE_PAGE'] or
                not config['VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES'] & DoublePage.AS_ONE_WIDE.value or
                self.__imagehandler.is_last_page(page)):
            return False

        for page in (page, page + 1):
            if not self.__imagehandler.page_is_available(page):
                return False
            pixbuf = self.__imagehandler.get_pixbuf(page - 1)
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
        current_page = self.__imagehandler.get_current_page()
        nb_pages = 2 if self.displayed_double else 1
        if current_page <= page < (current_page + nb_pages):
            self._displayed_double()
            self.draw_image(scroll_to=self.__last_scroll_destination)
            self._update_page_information()

    def _on_file_opened(self):
        self._displayed_double()
        self.__thumbnailsidebar.show()

        if config['STATUSBAR_FULLPATH']:
            self.__statusbar.set_archive_filename(self.__filehandler.get_path_to_base())
        else:
            self.__statusbar.set_archive_filename(self.__filehandler.get_base_filename())
        self.__statusbar.set_view_mode(self.is_manga_mode)
        self.__statusbar.set_filesize_archive(self.__filehandler.get_path_to_base())
        self.__statusbar.set_file_number(*self.__filehandler.get_file_number())
        self.__statusbar.update()

        self._update_title()

    def _on_file_closed(self):
        self.clear()
        self.__thumbnailsidebar.hide()
        self.__thumbnailsidebar.clear()

    def new_page(self, at_bottom: bool = False):
        """
        Draw a *new* page correctly (as opposed to redrawing the same image with a new size or whatever)
        """

        if not config['KEEP_TRANSFORMATION']:
            config['ROTATION'] = 0

        if at_bottom:
            scroll_to = Scroll.END.value
        else:
            scroll_to = Scroll.START.value

        self.draw_image(scroll_to=scroll_to)

    @Callback
    def page_changed(self):
        """
        Called on page change
        """

        self._displayed_double()
        self.__thumbnailsidebar.hide()
        self.__thumbnailsidebar.load_thumbnails()
        self._update_page_information()

    def set_page(self, num: int, at_bottom: bool = False):
        if num == self.__imagehandler.get_current_page():
            return
        self.__imagehandler.set_page(num)
        self.page_changed()
        self.new_page(at_bottom=at_bottom)

    def flip_page(self, number_of_pages: int, single_step: bool = False):
        if not self.__filehandler.get_file_loaded():
            return

        current_page = self.__imagehandler.get_current_page()
        current_number_of_pages = self.__imagehandler.get_number_of_pages()

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
                return self.__filehandler.open_archive_direction(forward=False)
            # Handle empty archive case.
            new_page = min(+1, current_number_of_pages)
        elif new_page > current_number_of_pages:
            if number_of_pages == +1:
                return self.__filehandler.open_archive_direction(forward=True)
            new_page = current_number_of_pages

        if new_page != current_page:
            self.set_page(new_page, at_bottom=(-1 == number_of_pages))

    def first_page(self):
        if self.__imagehandler.get_number_of_pages():
            self.set_page(1)

    def last_page(self):
        number_of_pages = self.__imagehandler.get_number_of_pages()
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
        self._update_page_information()
        self.draw_image()

    def change_manga_mode(self, *args):
        config['DEFAULT_MANGA_MODE'] = not config['DEFAULT_MANGA_MODE']
        self.is_manga_mode = config['DEFAULT_MANGA_MODE']
        self.__page_orientation = self.page_orientation()
        self.__statusbar.set_view_mode(self.is_manga_mode)
        self._update_page_information()
        self.draw_image()

    def is_fullscreen(self):
        window_state = self.get_window().get_state()
        return (window_state & Gdk.WindowState.FULLSCREEN) != 0

    def change_fullscreen(self, *args):
        # Disable action until transition if complete.

        if self.is_fullscreen():
            self.unfullscreen()

            self.__cursor_handler.auto_hide_off()

            # menu/status can only be hidden in fullscreen
            # if not hidden using .show() is the same as a NOOP
            self.__statusbar.show()
            self.__menubar.show()
        else:
            self.save_window_geometry()
            self.fullscreen()

            self.__cursor_handler.auto_hide_on()

            if config['FULLSCREEN_HIDE_STATUSBAR']:
                self.__statusbar.hide()
            if config['FULLSCREEN_HIDE_MENUBAR']:
                self.__menubar.hide()

        # No need to call draw_image explicitely,
        # as we'll be receiving a window state
        # change or resize event.

    def change_fit_mode_best(self, *args):
        self.change_zoom_mode(ZoomModes.BEST.value)

    def change_fit_mode_width(self, *args):
        self.change_zoom_mode(ZoomModes.WIDTH.value)

    def change_fit_mode_height(self, *args):
        self.change_zoom_mode(ZoomModes.HEIGHT.value)

    def change_fit_mode_size(self, *args):
        self.change_zoom_mode(ZoomModes.SIZE.value)

    def change_fit_mode_manual(self, *args):
        self.change_zoom_mode(ZoomModes.MANUAL.value)

    def change_zoom_mode(self, value: int = None):
        if value is not None:
            config['ZOOM_MODE'] = value
        self.__zoom.set_fit_mode(config['ZOOM_MODE'])
        self.__zoom.set_scale_up(config['STRETCH'])
        self.__zoom.reset_user_zoom()
        self.draw_image()

    def toggle_image_scaling(self):
        config['ENABLE_PIL_SCALING'] = not config['ENABLE_PIL_SCALING']
        self.draw_image()
        self.__statusbar.update_image_scaling()
        self.__statusbar.update()

    def change_image_scaling(self, step: int):
        if config['ENABLE_PIL_SCALING']:
            config_key = 'PIL_SCALING_FILTER'
            algos = ScalingPIL
        else:
            config_key = 'GDK_SCALING_FILTER'
            algos = ScalingGDK

        # inc/dec active algo, modulus loops algos to start on overflow
        # and end on underflow
        config[config_key] = algos((config[config_key] + step) % len(algos)).value

        self.draw_image()
        self.__statusbar.update_image_scaling()
        self.__statusbar.update()

    def change_stretch(self, *args):
        """
        Toggles stretching small images
        """

        config['STRETCH'] = not config['STRETCH']
        self.__zoom.set_scale_up(config['STRETCH'])
        self.draw_image()

    def open_dialog_about(self, *args):
        dialog = DialogChooser(DialogChoice.ABOUT)
        dialog.open_dialog(self)

    def open_dialog_enhance(self, *args):
        dialog = DialogChooser(DialogChoice.ENHANCE)
        dialog.open_dialog(self)

    def open_dialog_file_chooser(self, *args):
        dialog = DialogChooser(DialogChoice.FILECHOOSER)
        dialog.open_dialog(self)

    def open_dialog_keybindings(self, *args):
        dialog = DialogChooser(DialogChoice.KEYBINDINGS)
        dialog.open_dialog(self)

    def open_dialog_preference(self, *args):
        dialog = DialogChooser(DialogChoice.PREFERENCES)
        dialog.open_dialog(self)

    def open_dialog_properties(self, *args):
        dialog = DialogChooser(DialogChoice.PROPERTIES)
        dialog.open_dialog(self)

    def change_keep_transformation(self, *args):
        config['KEEP_TRANSFORMATION'] = not config['KEEP_TRANSFORMATION']

    def manual_zoom_in(self, *args):
        self.__zoom.zoom_in()
        self.draw_image()

    def manual_zoom_out(self, *args):
        self.__zoom.zoom_out()
        self.draw_image()

    def manual_zoom_original(self, *args):
        self.__zoom.reset_user_zoom()
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

        self.set_title(Mcomix.APP_NAME.value)
        self.__statusbar.set_message('')
        self.draw_image()

    def _displayed_double(self):
        """
        sets True if two pages are currently displayed
        """

        self.displayed_double = (self.__imagehandler.get_current_page() and
                                 config['DEFAULT_DOUBLE_PAGE'] and
                                 not self._get_virtual_double_page() and
                                 not self.__imagehandler.is_last_page())

    def get_visible_area_size(self):
        """
        :returns: a 2-tuple with the width and height of the visible part of the main layout area
        """

        dimensions = list(self.get_size())
        size = 0

        for widget, axis in self.__toggle_axis.items():
            size = widget.get_preferred_size()
            match axis:
                case ZoomAxis.WIDTH.value:
                    size = size.natural_size.width
                case ZoomAxis.HEIGHT.value:
                    size = size.natural_size.height
            dimensions[axis] -= size

        return tuple(dimensions)

    def _update_title(self):
        """
        Set the title acording to current state
        """

        self.set_title(f'{Mcomix.APP_NAME.value} [{self.__imagehandler.get_current_filename()}]')

    def extract_page(self, *args):
        self.__filesystem_hactions.extract_page()

    def move_file(self, *args):
        self.__filesystem_hactions.move_file()

    def trash_file(self, *args):
        self.__filesystem_hactions.trash_file()

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
        self.__keybindings.write_keybindings_file()
        self.__bookmark_backend.write_bookmarks_file()

        self.__filehandler.close_file()
