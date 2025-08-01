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

from gi.repository import GLib, Gdk, Gtk

import mcomix.image_tools as image_tools

from mcomix.bookmark_backend import BookmarkBackend
from mcomix.gui.cursor_handler import CursorHandler
from mcomix.file_handler import FileHandler
from mcomix.filesystem_actions import FileSystemActions
from mcomix.gui.input_handler import InputHandler
from mcomix.keybindings_manager import KeybindingManager
from mcomix.lib.events import Events, EventType
from mcomix.gui.menubar import Menubar
from mcomix.gui.dialog.pageselect import Pageselector
from mcomix.preferences import config
from mcomix.preferences_manager import PreferenceManager
from mcomix.view_state import ViewState
from mcomix.gui.statusbar import Statusbar
from mcomix.gui.thumbnail_sidebar import ThumbnailSidebar
from mcomix.gui.dialog.about import AboutDialog
from mcomix.gui.dialog.file_chooser import FileChooser
from mcomix.gui.dialog.keybindings import KeybindingEditorDialog
from mcomix.gui.dialog.preferences import PreferencesDialog
from mcomix.gui.dialog.properties import PropertiesDialog

from mcomix_compiled import Layout, ZoomModel, DoublePage, PackageInfo, Scroll, ZoomAxis

class MainWindow(Gtk.ApplicationWindow):
    """
    The main window, is created at start and terminates the program when closed
    """

    def __init__(self, open_path: list = None):
        super().__init__()

        # Load configuration.
        self.__preference_manager = PreferenceManager()
        self.__preference_manager.load_config_file()

        self.__events = Events()
        self.__events.add_event(EventType.FILE_OPENED, self._on_file_opened)
        self.__events.add_event(EventType.FILE_CLOSED, self._on_file_closed)
        self.__events.add_event(EventType.PAGE_AVAILABLE, self._page_available)
        self.__events.add_event(EventType.PAGE_CHANGED, self._page_changed)
        self.__events.add_event(EventType.DRAW_PAGE, self.draw_pages)
        # keyboard shortcut events
        self.__events.add_event(EventType.KB_PAGE_FLIP, self.flip_page)
        self.__events.add_event(EventType.KB_PAGE_FIRST, self.first_page)
        self.__events.add_event(EventType.KB_PAGE_LAST, self.last_page)
        self.__events.add_event(EventType.KB_CHANGE_ZOOM_MODE, self.change_zoom_mode)
        self.__events.add_event(EventType.KB_CHANGE_FULLSCREEN, self.change_fullscreen)
        self.__events.add_event(EventType.KB_MINIMIZE, self.minimize)
        self.__events.add_event(EventType.KB_EXIT, self.terminate_program)
        self.__events.add_event(EventType.KB_OPEN_PAGESELECTOR, self.page_select)
        self.__events.add_event(EventType.KB_PAGE_ROTATE, self.rotate_x)
        self.__events.add_event(EventType.KB_CHANGE_STRETCH, self.change_stretch)
        self.__events.add_event(EventType.KB_CHANGE_MANGA, self.change_manga_mode)
        self.__events.add_event(EventType.KB_CHANGE_DOUBLE, self.change_double_page)
        self.__events.add_event(EventType.KB_ZOOM_IN, self.manual_zoom_in)
        self.__events.add_event(EventType.KB_ZOOM_OUT, self.manual_zoom_out)
        self.__events.add_event(EventType.KB_ZOOM_ORIGINAL, self.manual_zoom_original)
        self.__events.add_event(EventType.KB_CHANGE_KEEP_TRANSFORMATION, self.change_keep_transformation)
        # Open Dialog
        self.__events.add_event(EventType.KB_OPEN_DIALOG_ABOUT, self.open_dialog_about)
        self.__events.add_event(EventType.KB_OPEN_DIALOG_FILECHOOSER, self.open_dialog_filechooser)
        self.__events.add_event(EventType.KB_OPEN_DIALOG_KEYBINDINGS, self.open_dialog_keybindings)
        self.__events.add_event(EventType.KB_OPEN_DIALOG_PREFERENCES, self.open_dialog_preferences)
        self.__events.add_event(EventType.KB_OPEN_DIALOG_PROPERTIES, self.open_dialog_properties)

        # Remember last scroll destination.
        self.__last_scroll_destination = Scroll.START

        self.__layout = Layout([[1, 1]], (1, 1), [1, 1], 0, 0)
        self.__waiting_for_redraw = False
        self.__page_orientation = self._page_orientation()

        self.__file_handler = FileHandler(self)
        self.__filesystem_actions = FileSystemActions(self)
        self.__bookmark_backend = BookmarkBackend(self)

        self.__thumbnailsidebar = ThumbnailSidebar(self)
        self.__thumbnailsidebar.hide()

        self.__statusbar = Statusbar()

        self.__zoom = ZoomModel()
        self.__zoom.set_fit_mode(config['ZOOM_MODE'])
        self.__zoom.set_scale_up(config['STRETCH'])
        self.__zoom.reset_user_zoom()

        self.__menubar = Menubar(self)

        self.__input_handler = InputHandler(self)

        self.__keybindings = KeybindingManager(self)

        self.__cursor_handler = CursorHandler(self)

        self.__main_layout = Gtk.Fixed()
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
        self.__images = [Gtk.Image(), Gtk.Image()]
        for img in self.__images:
            self.__main_layout.put(img, 0, 0)

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
        self.connect('key_press_event', self.__input_handler.key_press_event)
        self.connect('configure_event', self.__input_handler.resize_event)
        self.connect('window-state-event', self.__input_handler.window_state_event)

        self.__main_layout.connect('button_release_event', self.__input_handler.mouse_release_event)
        self.__main_layout.connect('scroll_event', self.__input_handler.scroll_wheel_event)
        self.__main_layout.connect('button_press_event', self.__input_handler.mouse_press_event)
        self.__main_layout.connect('motion_notify_event', self.__input_handler.mouse_move_event)
        self.__main_layout.connect('drag_data_received', self.__input_handler.drag_n_drop_event)
        self.__main_layout.connect('motion-notify-event', self.__cursor_handler.refresh)

        self.set_title(PackageInfo.APP_NAME)

        if config['DEFAULT_FULLSCREEN']:
            self.change_fullscreen()

        self.show_all()

        self.file_handler.open_file_init(open_path)

    @property
    def file_handler(self):
        return self.__file_handler

    @property
    def image_handler(self):
        return self.file_handler.image_handler

    @property
    def bookmark_backend(self):
        return self.__bookmark_backend

    @property
    def thumbnailsidebar(self):
        return self.__thumbnailsidebar

    @property
    def statusbar(self):
        return self.__statusbar

    @property
    def keybindings(self):
        return self.__keybindings

    @property
    def cursor_handler(self):
        return self.__cursor_handler

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

    def _page_orientation(self):
        if ViewState.is_manga_mode:
            return [-1, 1] # R->L
        else:
            return [1, 1] # L->R

    def _hide_images(self):
        # hides old images before showing new ones
        # also if in double page mode and only a single
        # image is going to be shown, prevents a ghost second image
        for i in self.__images:
            i.clear()

    def draw_pages(self, scroll_to=None):
        """
        Draw the current pages and update the titlebar and statusbar
        """

        if self.__waiting_for_redraw:
            # Don't stack up redraws.
            return

        self.__waiting_for_redraw = True
        GLib.idle_add(self._draw_pages, scroll_to, priority=GLib.PRIORITY_HIGH_IDLE)

    def _draw_pages(self, scroll_to: int):
        self._hide_images()

        if not self.file_handler.is_file_loaded():
            self.__thumbnailsidebar.hide()
            self.__waiting_for_redraw = False
            return

        self.__thumbnailsidebar.show()

        if not self.image_handler.is_page_available():
            # Save scroll destination for when the page becomes available.
            self.__last_scroll_destination = scroll_to
            self.__waiting_for_redraw = False
            return

        distribution_axis = ZoomAxis.DISTRIBUTION
        alignment_axis = ZoomAxis.ALIGNMENT
        # XXX limited to at most 2 pages
        pixbuf_count = 2 if ViewState.is_displaying_double else 1
        pixbuf_count_iter = range(pixbuf_count)
        pixbuf_list = list(self.image_handler.get_pixbufs(pixbuf_count))
        do_not_transform = [image_tools.disable_transform(x) for x in pixbuf_list]
        size_list = [[pixbuf.get_width(), pixbuf.get_height()] for pixbuf in pixbuf_list]

        # Rotation handling:
        # - apply manual rotation on whole page
        orientation = self.__page_orientation
        rotation_list = [0] * len(pixbuf_list)
        rotation = config['ROTATION'] % 360
        match rotation:
            case (90 | 270):
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

        self.__layout = Layout(scaled_sizes, viewport_size, orientation, distribution_axis, alignment_axis)

        content_boxes = self.__layout.get_content_boxes()

        for i in pixbuf_count_iter:
            rotation_list[i] = rotation

            pixbuf_list[i] = image_tools.fit_pixbuf_to_rectangle(pixbuf_list[i], scaled_sizes[i][0], scaled_sizes[i][1], rotation_list[i])

            image_tools.set_from_pixbuf(self.__images[i], pixbuf_list[i])

            self.__main_layout.move(self.__images[i], *content_boxes[i].get_position())

        # Reset orientation so scrolling behaviour is sane.
        self.__layout.set_orientation(self.__page_orientation)

        if scroll_to is not None:
            destination = (scroll_to,) * 2
            self.scroll_to_predefined(destination)

        # update statusbar
        self.__statusbar.set_resolution(scaled_sizes, size_list)
        self.__statusbar.update()

        self.__waiting_for_redraw = False

    def _update_page_information(self):
        """
        Updates the window with information that can be gathered
        even when the page pixbuf(s) aren't ready yet
        """

        page = self.image_handler.get_current_page()
        if not page:
            return

        filenames = self.image_handler.get_page_filename(page=page)
        filesizes = self.image_handler.get_page_filesize(page=page)

        filename = ', '.join(filenames)
        filesize = ', '.join(filesizes)

        self.__statusbar.set_page_number(page, self.image_handler.get_number_of_pages())
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
            page = self.image_handler.get_current_page()

        if (page == 1
                and int(config['VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES']) & int(DoublePage.AS_ONE_TITLE)
                and self.file_handler.is_archive()):
            return True

        if (not config['DEFAULT_DOUBLE_PAGE']
                or not int(config['VIRTUAL_DOUBLE_PAGE_FOR_FITTING_IMAGES']) & int(DoublePage.AS_ONE_WIDE)
                or self.image_handler.is_last_page(page)):
            return False

        for page in (page, page + 1):
            if not self.image_handler.is_page_available(page):
                return False
            width, height = self.image_handler.get_page_size(page)
            if width > height:
                return True

        return False

    def _page_available(self, page: int):
        """
        Called whenever a new page is ready for displaying
        """

        # Refresh display when currently opened page becomes available.
        current_page = self.image_handler.get_current_page()
        nb_pages = 2 if ViewState.is_displaying_double else 1
        if current_page <= page < (current_page + nb_pages):
            self._displayed_double()
            self.__events.run_events(EventType.DRAW_PAGE, {'scroll_to': self.__last_scroll_destination})
            self._update_page_information()

    def _on_file_opened(self):
        self._displayed_double()
        self.__thumbnailsidebar.show()

        if config['STATUSBAR_FULLPATH']:
            self.__statusbar.set_archive_filename(self.file_handler.get_base_path())
        else:
            self.__statusbar.set_archive_filename(self.file_handler.get_base_path().name)
        self.__statusbar.set_view_mode()
        self.__statusbar.set_filesize_archive(self.file_handler.get_base_path())
        self.__statusbar.set_file_number(*self.file_handler.get_file_number())
        self.__statusbar.update()

        self._update_title()

    def _on_file_closed(self):
        self.set_title(PackageInfo.APP_NAME)
        self._hide_images()
        self.__statusbar.set_message('')
        self.__thumbnailsidebar.hide()
        self.__thumbnailsidebar.clear()

    def _new_page(self, at_bottom: bool = False):
        """
        Draw a *new* page correctly (as opposed to redrawing the same image with a new size or whatever)
        """

        if not config['KEEP_TRANSFORMATION']:
            config['ROTATION'] = 0

        if at_bottom:
            scroll_to = Scroll.END
        else:
            scroll_to = Scroll.START

        self.__events.run_events(EventType.DRAW_PAGE, {'scroll_to': scroll_to})

    def page_changed(self):
        """
        Called on page change
        """

        self.__events.run_events(EventType.PAGE_CHANGED)

    def _page_changed(self):
        self._displayed_double()
        self.__thumbnailsidebar.hide()
        self.__thumbnailsidebar.load_thumbnails()
        self._update_page_information()

    def set_page(self, num: int, at_bottom: bool = False):
        """
        Draws a *new* page (as opposed to redrawing the same image with a new size or whatever)
        """

        if num == self.image_handler.get_current_page():
            return

        self.image_handler.set_page(num)
        self.page_changed()
        self._new_page(at_bottom=at_bottom)

    def flip_page(self, number_of_pages: int, single_step: bool = False):
        if not self.file_handler.is_file_loaded():
            return

        current_page = self.image_handler.get_current_page()
        current_number_of_pages = self.image_handler.get_number_of_pages()

        new_page = current_page + number_of_pages
        if (abs(number_of_pages) == 1 and
                not single_step and
                config['DEFAULT_DOUBLE_PAGE'] and
                config['DOUBLE_STEP_IN_DOUBLE_PAGE_MODE']):
            if number_of_pages == 1 and not self._get_virtual_double_page():
                new_page += 1
            elif number_of_pages == -1 and not self._get_virtual_double_page(new_page - 1):
                new_page -= 1

        if new_page <= 0:
            # Only switch to previous page when flipping one page before the
            # first one. (Note: check for (page number <= 1) to handle empty
            # archive case).
            if number_of_pages == -1 and current_page <= 1:
                return self.file_handler.open_archive_direction(forward=False)
            # Handle empty archive case.
            new_page = min(1, current_number_of_pages)
        elif new_page > current_number_of_pages:
            if number_of_pages == 1:
                return self.file_handler.open_archive_direction(forward=True)
            new_page = current_number_of_pages

        if new_page != current_page:
            self.set_page(new_page, at_bottom=(-1 == number_of_pages))

    def first_page(self):
        if self.image_handler.get_number_of_pages():
            self.set_page(1)

    def last_page(self):
        number_of_pages = self.image_handler.get_number_of_pages()
        if number_of_pages:
            self.set_page(number_of_pages)

    def page_select(self):
        Pageselector(self)

    def rotate_x(self, rotation: int):
        config['ROTATION'] = (config['ROTATION'] + rotation) % 360
        self.__events.run_events(EventType.DRAW_PAGE)

    def change_double_page(self):
        config['DEFAULT_DOUBLE_PAGE'] = not config['DEFAULT_DOUBLE_PAGE']
        self._displayed_double()
        self._update_page_information()
        self.__events.run_events(EventType.DRAW_PAGE)

    def change_manga_mode(self):
        config['DEFAULT_MANGA_MODE'] = not config['DEFAULT_MANGA_MODE']
        ViewState.is_manga_mode = config['DEFAULT_MANGA_MODE']
        self.__page_orientation = self._page_orientation()
        self.__statusbar.set_view_mode()
        self._update_page_information()
        self.__events.run_events(EventType.DRAW_PAGE)

    def is_fullscreen(self):
        window_state = self.get_window().get_state()
        return (window_state & Gdk.WindowState.FULLSCREEN) != 0

    def change_fullscreen(self):
        # Disable action until transition if complete.

        if self.is_fullscreen():
            self.unfullscreen()

            self.__cursor_handler.auto_hide_off()

            # menu/status can only be hidden in fullscreen
            # if not hidden using .show() is the same as a NOOP
            self.__statusbar.show()
            self.__menubar.show()
        else:
            self.fullscreen()

            self.__cursor_handler.auto_hide_on()

            if config['FULLSCREEN_HIDE_STATUSBAR']:
                self.__statusbar.hide()
            if config['FULLSCREEN_HIDE_MENUBAR']:
                self.__menubar.hide()

        # No need to call draw_pages explicitely,
        # as we'll be receiving a window state
        # change or resize event.

    def change_zoom_mode(self, value: int = None):
        if value is not None:
            config['ZOOM_MODE'] = value
        self.__zoom.set_fit_mode(config['ZOOM_MODE'])
        self.__zoom.set_scale_up(config['STRETCH'])
        self.__zoom.reset_user_zoom()
        self.__events.run_events(EventType.DRAW_PAGE)

    def change_stretch(self):
        """
        Toggles stretching small images
        """

        config['STRETCH'] = not config['STRETCH']
        self.__zoom.set_scale_up(config['STRETCH'])
        self.__events.run_events(EventType.DRAW_PAGE)

    def open_dialog_about(self):
        AboutDialog(self)

    def open_dialog_filechooser(self):
        FileChooser(self)

    def open_dialog_keybindings(self):
        KeybindingEditorDialog(self)

    def open_dialog_preferences(self):
        PreferencesDialog(self)

    def open_dialog_properties(self):
        PropertiesDialog(self)

    def change_keep_transformation(self):
        config['KEEP_TRANSFORMATION'] = not config['KEEP_TRANSFORMATION']

    def manual_zoom_in(self):
        self.__zoom.zoom_in()
        self.__events.run_events(EventType.DRAW_PAGE)

    def manual_zoom_out(self):
        self.__zoom.zoom_out()
        self.__events.run_events(EventType.DRAW_PAGE)

    def manual_zoom_original(self):
        self.__zoom.reset_user_zoom()
        self.__events.run_events(EventType.DRAW_PAGE)

    def scroll_to_predefined(self, destination: tuple[Scroll]):
        self.__layout.scroll_to_predefined(destination)
        viewport_position = self.__layout.get_viewport_box().get_position()
        self.__hadjust.set_value(viewport_position[0])  # 2D only
        self.__vadjust.set_value(viewport_position[1])  # 2D only

    def _displayed_double(self):
        """
        sets True if two pages are currently displayed
        """

        ViewState.is_displaying_double = (
            self.image_handler.get_current_page() and
            config['DEFAULT_DOUBLE_PAGE'] and
            not self._get_virtual_double_page() and
            not self.image_handler.is_last_page()
        )

    def get_visible_area_size(self):
        """
        :returns: a 2-tuple with the width and height of the visible part of the main layout area
        """

        dimensions = list(self.get_size())

        # Each widget "eats" part of the main layout visible area.

        # this widget eats width
        if self.__thumbnailsidebar.is_visible():
            size = self.__thumbnailsidebar.get_allocated_width()
            dimensions[0] -= size

        # this widget eats height
        if self.__menubar.is_visible():
            size = self.__menubar.get_allocated_height()
            dimensions[1] -= size

        # this widget eats height
        if self.__statusbar.is_visible():
            size = self.__statusbar.get_allocated_height()
            dimensions[1] -= size

        return dimensions

    def _update_title(self):
        """
        Set the title acording to current state
        """

        self.set_title(f'{PackageInfo.APP_NAME} [{self.file_handler.get_real_path()}]')

    def minimize(self):
        """
        Minimizes the MComix window
        """

        self.iconify()

    def terminate_program(self, *args):
        """
        Run clean-up tasks and exit the program
        """

        self.hide()

        if Gtk.main_level() > 0:
            Gtk.main_quit()

        # write config file
        self.__preference_manager.write_config_file()
        self.__keybindings.write_keybindings_file()
        self.__bookmark_backend.write_bookmarks_file()

        self.file_handler.close_file()
