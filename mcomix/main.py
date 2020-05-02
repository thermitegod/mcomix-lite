"""main.py - Main window"""

import shutil
from pathlib import Path

from gi.repository import GLib, Gdk, Gtk
from send2trash import send2trash

from mcomix import bookmark_backend, callback, constants, cursor_handler, enhance_backend, event, file_handler, icons, \
    image_handler, image_tools, keybindings, layout, lens, message_dialog, pageselect, preferences, status, \
    thumbbar, tools, ui, zoom
from mcomix.preferences import prefs


class MainWindow(Gtk.Window):
    """The main window, is created at start and terminates the program when closed"""

    def __init__(self, fullscreen=False, manga_mode=False, double_page=False,
                 zoom_mode=None, open_path=None, open_page=1):
        super(MainWindow, self).__init__(type=Gtk.WindowType.TOPLEVEL)
        # ----------------------------------------------------------------
        # Attributes
        # ----------------------------------------------------------------
        # Used to detect window fullscreen state transitions.
        self.was_fullscreen = False
        self.is_manga_mode = False
        self.previous_size = (None, None)
        #: Used to remember if changing to fullscreen enabled 'Hide all'
        self.__hide_all_forced = False
        # Remember last scroll destination.
        self.__last_scroll_destination = constants.SCROLL_TO_START

        self.__layout = _dummy_layout()
        self.__spacing = 2
        self.__waiting_for_redraw = False

        self.__main_layout = Gtk.Layout()
        # Wrap main layout into an event box so
        # we  can change its background color.
        self.__event_box = Gtk.EventBox()
        self.__event_box.add(self.__main_layout)
        self.__event_handler = event.EventHandler(self)
        self.__vadjust = self.__main_layout.get_vadjustment()
        self.__hadjust = self.__main_layout.get_hadjustment()
        self.__scroll = (
            Gtk.Scrollbar.new(Gtk.Orientation.HORIZONTAL, self.__hadjust),
            Gtk.Scrollbar.new(Gtk.Orientation.VERTICAL, self.__vadjust),
        )

        self.__bg_color = None

        self.filehandler = file_handler.FileHandler(self)
        self.filehandler.file_closed += self._on_file_closed
        self.filehandler.file_opened += self._on_file_opened
        self.imagehandler = image_handler.ImageHandler(self)
        self.imagehandler.page_available += self._page_available
        self.thumbnailsidebar = thumbbar.ThumbnailSidebar(self)

        self.statusbar = status.Statusbar()
        self.cursor_handler = cursor_handler.CursorHandler(self)
        self.enhancer = enhance_backend.ImageEnhancer(self)
        self.lens = lens.MagnifyingLens(self)
        self.zoom = zoom.ZoomModel()
        self.uimanager = ui.MainUI(self)
        self.menubar = self.uimanager.get_widget('/Menu')
        self.popup = self.uimanager.get_widget('/Popup')
        self.actiongroup = self.uimanager.get_action_groups()[0]

        self.images = [Gtk.Image(), Gtk.Image()]  # XXX limited to at most 2 pages

        # ----------------------------------------------------------------
        # Setup
        # ----------------------------------------------------------------
        self.set_title(constants.APPNAME)
        self.restore_window_geometry()

        # Hook up keyboard shortcuts
        self.__event_handler.register_key_events()

        for img in self.images:
            self.__main_layout.put(img, 0, 0)
        self.set_bg_color(prefs['bg color'])

        table = Gtk.Table(n_rows=2, n_columns=2, homogeneous=False)
        table.attach(self.thumbnailsidebar, 0, 1, 2, 5, Gtk.AttachOptions.FILL,
                     Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, 0, 0)

        table.attach(self.__event_box, 1, 2, 2, 3, Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND,
                     Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, 0, 0)
        table.attach(self.__scroll[constants.HEIGHT_AXIS], 2, 3, 2, 3, Gtk.AttachOptions.FILL | Gtk.AttachOptions.SHRINK,
                     Gtk.AttachOptions.FILL | Gtk.AttachOptions.SHRINK, 0, 0)
        table.attach(self.__scroll[constants.WIDTH_AXIS], 1, 2, 4, 5, Gtk.AttachOptions.FILL | Gtk.AttachOptions.SHRINK,
                     Gtk.AttachOptions.FILL, 0, 0)
        table.attach(self.menubar, 0, 3, 0, 1, Gtk.AttachOptions.FILL | Gtk.AttachOptions.SHRINK,
                     Gtk.AttachOptions.FILL, 0, 0)
        table.attach(self.statusbar, 0, 3, 5, 6, Gtk.AttachOptions.FILL | Gtk.AttachOptions.SHRINK,
                     Gtk.AttachOptions.FILL, 0, 0)

        if prefs['default double page'] or double_page:
            self.actiongroup.get_action('double_page').activate()

        if prefs['default manga mode'] or manga_mode:
            self.actiongroup.get_action('manga_mode').activate()

        # Determine zoom mode. If zoom_mode is passed, it overrides
        # the zoom mode preference.
        zoom_actions = {constants.ZOOM_MODE_BEST: 'best_fit_mode',
                        constants.ZOOM_MODE_WIDTH: 'fit_width_mode',
                        constants.ZOOM_MODE_HEIGHT: 'fit_height_mode',
                        constants.ZOOM_MODE_SIZE: 'fit_size_mode',
                        constants.ZOOM_MODE_MANUAL: 'fit_manual_mode'}

        if zoom_mode is not None:
            zoom_action = zoom_actions[zoom_mode]
        else:
            zoom_action = zoom_actions[prefs['zoom mode']]

        self.actiongroup.get_action(zoom_action).activate()

        if prefs['stretch']:
            self.actiongroup.get_action('stretch').activate()

        if prefs['keep transformation']:
            prefs['keep transformation'] = False
            self.actiongroup.get_action('keep_transformation').activate()
        else:
            prefs['rotation'] = 0
            prefs['vertical flip'] = False
            prefs['horizontal flip'] = False

        # List of "toggles" than can be shown/hidden by the user.
        self.__toggle_list = (
            # Preference        Action        Widget(s)
            ('show menubar', 'menubar', (self.menubar,)),
            ('show scrollbar', 'scrollbar', self.__scroll),
            ('show statusbar', 'statusbar', (self.statusbar,)),
            ('show thumbnails', 'thumbnails', (self.thumbnailsidebar,)),
        )

        # Each "toggle" widget "eats" part of the main layout visible area.
        self.__toggle_axis = {
            self.thumbnailsidebar: constants.WIDTH_AXIS,
            self.__scroll[constants.HEIGHT_AXIS]: constants.WIDTH_AXIS,
            self.__scroll[constants.WIDTH_AXIS]: constants.HEIGHT_AXIS,
            self.statusbar: constants.HEIGHT_AXIS,
            self.menubar: constants.HEIGHT_AXIS,
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

        if prefs['default fullscreen'] or fullscreen:
            toggleaction = self.actiongroup.get_action('fullscreen')
            toggleaction.set_active(True)

        if open_path is not None:
            self.filehandler.open_file(open_path)

        if prefs['hide cursor']:
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

    def draw_image(self, scroll_to=None):
        """Draw the current pages and update the titlebar and statusbar"""
        # FIXME: what if scroll_to is different?
        if not self.__waiting_for_redraw:  # Don't stack up redraws.
            self.__waiting_for_redraw = True
            GLib.idle_add(self._draw_image, scroll_to, priority=GLib.PRIORITY_HIGH_IDLE)

    def _update_toggle_preference(self, preference, toggleaction):
        """Update "toggle" widget corresponding <preference>.
        Note: the widget visibily itself is left unchanged"""
        prefs[preference] = toggleaction.get_active()
        if preference == 'hide all':
            self.update_toggles_sensitivity()
        # Since the size of the drawing area is dependent
        # on the visible "toggles", redraw the page.
        self.draw_image()

    def _should_toggle_be_visible(self, preference):
        """Return <True> if "toggle" widget for <preference> should be visible"""
        if self.is_fullscreen:
            visible = not prefs['hide all in fullscreen'] and not prefs['hide all']
        else:
            visible = not prefs['hide all']
        visible &= prefs[preference]
        if preference == 'show thumbnails':
            visible &= self.filehandler.get_file_loaded()
            visible &= self.imagehandler.get_number_of_pages() > 0
        return visible

    def update_toggles_sensitivity(self):
        """Update each "toggle" widget sensitivity"""
        sensitive = True
        if prefs['hide all'] or (prefs['hide all in fullscreen'] and self.is_fullscreen):
            sensitive = False
        for preference, action, widget_list in self.__toggle_list:
            self.actiongroup.get_action(action).set_sensitive(sensitive)

    def _update_toggles_visibility(self):
        """Update each "toggle" widget visibility"""
        for preference, action, widget_list in self.__toggle_list:
            should_be_visible = self._should_toggle_be_visible(preference)
            for widget in widget_list:
                # No change in visibility?
                if should_be_visible != widget.get_visible():
                    (widget.show if should_be_visible else widget.hide)()

    def _draw_image(self, scroll_to):
        self._update_toggles_visibility()

        if not self.filehandler.get_file_loaded():
            self._clear_main_area()
            self.__waiting_for_redraw = False
            return False

        if self.imagehandler.page_is_available():
            distribution_axis = constants.DISTRIBUTION_AXIS
            alignment_axis = constants.ALIGNMENT_AXIS
            pixbuf_count = 2 if self.displayed_double() else 1  # XXX limited to at most 2 pages
            pixbuf_list = list(self.imagehandler.get_pixbufs(pixbuf_count))
            do_not_transform = [image_tools.disable_transform(x) for x in pixbuf_list]
            size_list = [[pixbuf.get_width(), pixbuf.get_height()] for pixbuf in pixbuf_list]

            if self.is_manga_mode:
                orientation = constants.MANGA_ORIENTATION
            else:
                orientation = constants.WESTERN_ORIENTATION

            # Rotation handling:
            # - apply Exif rotation on individual images
            # - apply automatic rotation (size based) on whole page
            # - apply manual rotation on whole page
            if prefs['auto rotate from exif']:
                rotation_list = [image_tools.get_implied_rotation(pixbuf) for pixbuf in pixbuf_list]
            else:
                rotation_list = [0] * len(pixbuf_list)
            virtual_size = [0, 0]
            for i in range(pixbuf_count):
                if rotation_list[i] in (90, 270):
                    size_list[i].reverse()
                size = size_list[i]
                virtual_size[distribution_axis] += size[distribution_axis]
                virtual_size[alignment_axis] = max(virtual_size[alignment_axis], size[alignment_axis])
            rotation = (self._get_size_rotation(*virtual_size) + prefs['rotation']) % 360
            if rotation in (90, 270):
                distribution_axis, alignment_axis = alignment_axis, distribution_axis
                orientation = list(orientation)
                orientation.reverse()
                for i in range(pixbuf_count):
                    size_list[i].reverse()
            elif rotation in (180, 270):
                orientation = tools.vector_opposite(orientation)
            for i in range(pixbuf_count):
                rotation_list[i] = (rotation_list[i] + rotation) % 360
            if prefs['vertical flip']:
                orientation = tools.vector_opposite(orientation)
            if prefs['horizontal flip']:
                orientation = tools.vector_opposite(orientation)

            viewport_size = ()  # dummy
            expand_area = False
            scrollbar_requests = [False] * len(self.__scroll)
            # Visible area size is recomputed depending on scrollbar visibility
            while True:
                self._show_scrollbars(scrollbar_requests)
                if (new_viewport_size := self.get_visible_area_size()) == viewport_size:
                    break
                viewport_size = new_viewport_size
                zoom_dummy_size = list(viewport_size)
                if (dasize := zoom_dummy_size[distribution_axis] - self.__spacing * (pixbuf_count - 1)) <= 0:
                    dasize = 1
                zoom_dummy_size[distribution_axis] = dasize
                scaled_sizes = self.zoom.get_zoomed_size(size_list, zoom_dummy_size,
                                                         distribution_axis, do_not_transform)

                self.__layout = layout.FiniteLayout(
                        scaled_sizes, viewport_size, orientation, self.__spacing,
                        expand_area, distribution_axis, alignment_axis)

                union_scaled_size = self.__layout.get_union_box().get_size()

                scrollbar_requests = [(old or new) for old, new in zip(
                        scrollbar_requests, tools.smaller(viewport_size, union_scaled_size))]

                if len(tuple(filter(None, scrollbar_requests))) > 1 and not expand_area:
                    expand_area = True
                    viewport_size = ()  # start anew

            for i in range(pixbuf_count):
                pixbuf_list[i] = image_tools.fit_pixbuf_to_rectangle(
                        pixbuf_list[i], scaled_sizes[i], rotation_list[i])

            for i in range(pixbuf_count):
                pixbuf_list[i] = image_tools.trans_pixbuf(
                        pixbuf_list[i],
                        flip=prefs['vertical flip'],
                        flop=prefs['horizontal flip'])
                pixbuf_list[i] = self.enhancer.enhance(pixbuf_list[i])

            for i in range(pixbuf_count):
                image_tools.set_from_pixbuf(self.images[i], pixbuf_list[i])

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
            if self.is_manga_mode:
                self.__layout.set_orientation(constants.MANGA_ORIENTATION)
            else:
                self.__layout.set_orientation(constants.WESTERN_ORIENTATION)

            if scroll_to is not None:
                if constants.SCROLL_TO_START == scroll_to:
                    index = constants.FIRST_INDEX
                elif constants.SCROLL_TO_END == scroll_to:
                    index = constants.LAST_INDEX
                else:
                    index = None
                destination = (scroll_to,) * 2
                self.scroll_to_predefined(destination, index)

            self.__main_layout.get_bin_window().thaw_updates()
        else:
            # Save scroll destination for when the page becomes available.
            self.__last_scroll_destination = scroll_to
            # If the pixbuf for the current page(s) isn't available clear old pixbufs.
            self._clear_main_area()
            self._show_scrollbars([False] * len(self.__scroll))

        self.__waiting_for_redraw = False

        return False

    def _update_page_information(self):
        """Updates the window with information that can be gathered
        even when the page pixbuf(s) aren't ready yet"""
        if not (page_number := self.imagehandler.get_current_page()):
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
        self.statusbar.set_root(self.filehandler.get_base_filename())
        self.statusbar.set_filesize(filesize)
        self.statusbar.update()
        self.update_title()

    @staticmethod
    def _get_size_rotation(width, height):
        """Determines the rotation to be applied. Returns the degree of rotation (0, 90, 180, 270)"""
        size_rotation = 0

        if (height > width and
                prefs['auto rotate depending on size'] in
                (constants.AUTOROTATE_HEIGHT_90, constants.AUTOROTATE_HEIGHT_270)):
            if prefs['auto rotate depending on size'] == constants.AUTOROTATE_HEIGHT_90:
                size_rotation = 90
            else:
                size_rotation = 270
        elif (width > height and
              prefs['auto rotate depending on size'] in
              (constants.AUTOROTATE_WIDTH_90, constants.AUTOROTATE_WIDTH_270)):
            if prefs['auto rotate depending on size'] == constants.AUTOROTATE_WIDTH_90:
                size_rotation = 90
            else:
                size_rotation = 270

        return size_rotation

    def _page_available(self, page):
        """Called whenever a new page is ready for displaying"""
        # Refresh display when currently opened page becomes available.
        current_page = self.imagehandler.get_current_page()
        nb_pages = 2 if self.displayed_double() else 1
        if current_page <= page < (current_page + nb_pages):
            self.draw_image(scroll_to=self.__last_scroll_destination)
            self._update_page_information()

        # Use first page as application icon when opening archives.
        if (page == 1
                and self.filehandler.get_archive_type() is not None
                and prefs['archive thumbnail as icon']):
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
        self.set_icon_list(icons.mcomix_icons())

    def new_page(self, at_bottom=False):
        """Draw a *new* page correctly (as opposed to redrawing the same image with a new size or whatever)"""
        if not prefs['keep transformation']:
            prefs['rotation'] = 0
            prefs['horizontal flip'] = False
            prefs['vertical flip'] = False

        if at_bottom:
            scroll_to = constants.SCROLL_TO_END
        else:
            scroll_to = constants.SCROLL_TO_START

        self.draw_image(scroll_to=scroll_to)

    @callback.Callback
    def page_changed(self):
        """Called on page change"""
        self.thumbnailsidebar.load_thumbnails()
        self._update_page_information()

    def set_page(self, num, at_bottom=False):
        if num == self.imagehandler.get_current_page():
            return
        self.imagehandler.set_page(num)
        self.page_changed()
        self.new_page(at_bottom=at_bottom)

    def next_book(self):
        archive_open = self.filehandler.get_archive_type() is not None
        next_archive_opened = False
        if prefs['auto open next archive']:
            next_archive_opened = self.filehandler.open_next_archive()

        # If "Auto open next archive" is disabled, do not go to the next
        # directory if current file was an archive.
        if not next_archive_opened and \
                prefs['auto open next directory'] and \
                (not archive_open or prefs['auto open next archive']):
            self.filehandler.open_next_directory()

    def previous_book(self):
        archive_open = self.filehandler.get_archive_type() is not None
        previous_archive_opened = False
        if prefs['auto open next archive']:
            previous_archive_opened = self.filehandler.open_previous_archive()

        # If "Auto open next archive" is disabled, do not go to the previous
        # directory if current file was an archive.
        if not previous_archive_opened and \
                prefs['auto open next directory'] and \
                (not archive_open or prefs['auto open next archive']):
            self.filehandler.open_previous_directory()

    def flip_page(self, step, single_step=False):
        if not self.filehandler.get_file_loaded():
            return

        current_page = self.imagehandler.get_current_page()
        number_of_pages = self.imagehandler.get_number_of_pages()

        new_page = current_page + step
        if (abs(step) == 1 and
                not single_step and
                prefs['default double page'] and
                prefs['double step in double page mode']):
            if step == +1 and not self.imagehandler.get_virtual_double_page():
                new_page += 1
            elif step == -1 and not self.imagehandler.get_virtual_double_page(new_page - 1):
                new_page -= 1

        if new_page <= 0:
            # Only switch to previous page when flipping one page before the
            # first one. (Note: check for (page number <= 1) to handle empty
            # archive case).
            if step == -1 and current_page <= 1:
                return self.previous_book()
            # Handle empty archive case.
            new_page = min(1, number_of_pages)
        elif new_page > number_of_pages:
            if step == 1:
                return self.next_book()
            new_page = number_of_pages

        if new_page != current_page:
            self.set_page(new_page, at_bottom=(-1 == step))

    def first_page(self):
        if self.imagehandler.get_number_of_pages():
            self.set_page(1)

    def last_page(self):
        if number_of_pages := self.imagehandler.get_number_of_pages():
            self.set_page(number_of_pages)

    def page_select(self, *args):
        pageselect.Pageselector(self)

    def rotate_90(self, *args):
        prefs['rotation'] = (prefs['rotation'] + 90) % 360
        self.draw_image()

    def rotate_180(self, *args):
        prefs['rotation'] = (prefs['rotation'] + 180) % 360
        self.draw_image()

    def rotate_270(self, *args):
        prefs['rotation'] = (prefs['rotation'] + 270) % 360
        self.draw_image()

    def flip_horizontally(self, *args):
        prefs['horizontal flip'] = not prefs['horizontal flip']
        self.draw_image()

    def flip_vertically(self, *args):
        prefs['vertical flip'] = not prefs['vertical flip']
        self.draw_image()

    def change_double_page(self, toggleaction):
        prefs['default double page'] = toggleaction.get_active()
        self._update_page_information()
        self.draw_image()

    def change_manga_mode(self, toggleaction):
        prefs['default manga mode'] = toggleaction.get_active()
        self.is_manga_mode = toggleaction.get_active()
        self._update_page_information()
        self.draw_image()

    @property
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
            prefs['zoom mode'] = radioaction.get_current_value()
        self.zoom.set_fit_mode(prefs['zoom mode'])
        self.zoom.set_scale_up(prefs['stretch'])
        self.zoom.reset_user_zoom()
        self.draw_image()

    def change_autorotation(self, radioaction=None, *args):
        """Switches between automatic rotation modes, depending on which
        radiobutton is currently activated"""
        if radioaction:
            prefs['auto rotate depending on size'] = radioaction.get_current_value()
        self.draw_image()

    def change_stretch(self, toggleaction, *args):
        """Toggles stretching small images"""
        prefs['stretch'] = toggleaction.get_active()
        self.zoom.set_scale_up(prefs['stretch'])
        self.draw_image()

    def change_menubar_visibility(self, toggleaction):
        self._update_toggle_preference('show menubar', toggleaction)

    def change_statusbar_visibility(self, toggleaction):
        self._update_toggle_preference('show statusbar', toggleaction)

    def change_scrollbar_visibility(self, toggleaction):
        self._update_toggle_preference('show scrollbar', toggleaction)

    def change_thumbnails_visibility(self, toggleaction):
        self._update_toggle_preference('show thumbnails', toggleaction)

    def change_hide_all(self, toggleaction):
        self._update_toggle_preference('hide all', toggleaction)

    @staticmethod
    def change_keep_transformation(*args):
        prefs['keep transformation'] = not prefs['keep transformation']

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
        """Enables scroll bars depending on requests and preferences"""
        limit = self._should_toggle_be_visible('show scrollbar')
        for idx, item in enumerate(self.__scroll):
            if limit and request[idx]:
                self.__scroll[idx].show()
            else:
                self.__scroll[idx].hide()

    def scroll(self, x, y):
        """Scroll <x> px horizontally and <y> px vertically. If <bound> is
        'first' or 'second', we will not scroll out of the first or second
        page respectively (dependent on manga mode). The <bound> argument
        only makes sense in double page mode.
        Return True if call resulted in new adjustment values, False otherwise"""
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

    def scroll_to_predefined(self, destination, index=None):
        self.__layout.scroll_to_predefined(destination, index)
        viewport_position = self.__layout.get_viewport_box().get_position()
        self.__hadjust.set_value(viewport_position[0])  # 2D only
        self.__vadjust.set_value(viewport_position[1])  # 2D only
        self.__scroll[0].queue_resize_no_redraw()
        self.__scroll[1].queue_resize_no_redraw()

    def clear(self):
        """Clear the currently displayed data (i.e. "close" the file)"""
        self.set_title(constants.APPNAME)
        self.statusbar.set_message('')
        self.draw_image()

    def _clear_main_area(self):
        for i in self.images:
            i.hide()
            i.clear()

        self._show_scrollbars([False] * len(self.__scroll))
        self.__layout = _dummy_layout()
        self.__main_layout.set_size(*self.__layout.get_union_box().get_size())
        self.set_bg_color(prefs['bg color'])

    def displayed_double(self):
        """Return True if two pages are currently displayed"""
        return (self.imagehandler.get_current_page() and
                prefs['default double page'] and
                not self.imagehandler.get_virtual_double_page() and
                self.imagehandler.get_current_page() != self.imagehandler.get_number_of_pages())

    def get_visible_area_size(self):
        """Return a 2-tuple with the width and height of the visible part of the main layout area"""
        dimensions = list(self.get_size())

        for preference, action, widget_list in self.__toggle_list:
            for widget in widget_list:
                if widget.get_visible():
                    axis = self.__toggle_axis[widget]
                    requisition = widget.size_request()
                    if constants.WIDTH_AXIS == axis:
                        size = requisition.width
                    elif constants.HEIGHT_AXIS == axis:
                        size = requisition.height
                    dimensions[axis] -= size

        return tuple(dimensions)

    def set_cursor(self, mode):
        """Set the cursor on the main layout area to <mode>. You should
        probably use the cursor_handler instead of using this method directly"""
        self.__main_layout.get_bin_window().set_cursor(mode)

    def update_title(self):
        """Set the title acording to current state"""
        self.set_title(' '.join([f'[{self.statusbar.get_page_number()}]',
                                 self.imagehandler.get_current_filename()]))

    def set_bg_color(self, color):
        """Set the background color to <color>. color is a sequence in the
        format (r, g, b). Values are 16-bit"""
        self.__event_box.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(*color))
        if prefs['thumbnail bg uses main color']:
            self.thumbnailsidebar.change_thumbnail_background_color(prefs['bg color'])
        self.__bg_color = color

    def get_bg_color(self):
        return self.__bg_color

    def extract_page(self, *args):
        """Derive some sensible filename (archive name + _ + filename should do) and offer
        the user the choice to save the current page with the selected name"""
        if self.filehandler.get_archive_type() is not None:
            archive_name = self.filehandler.get_current_filename()
            file_name = self.imagehandler.get_path_to_page()
            suggested_name = f'{Path(archive_name).stem}_{file_name}'
        else:
            suggested_name = self.imagehandler.get_path_to_page()

        save_dialog = Gtk.FileChooserDialog(title='Save page as', action=Gtk.FileChooserAction.SAVE)
        save_dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT, Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        save_dialog.set_transient_for(self)
        save_dialog.set_do_overwrite_confirmation(True)
        save_dialog.set_current_name(suggested_name.encode('utf-8'))

        if save_dialog.run() == Gtk.ResponseType.ACCEPT and save_dialog.get_filename():
            shutil.copy(self.imagehandler.get_path_to_page(), save_dialog.get_filename())

        save_dialog.destroy()

    def move_file(self, action=None, *args):
        """The currently opened file/archive will be moved to prefs['move file']
        or
        The currently opened file/archive will be trashed after showing a confirmation dialog"""
        if action is None:
            return None

        current_file = self.imagehandler.get_real_path()

        def file_action():
            if action == 'move_file':
                Path.rename(current_file, target_file)
            elif action == 'delete':
                send2trash(current_file)

        if action == 'move_file':
            current_file = Path(current_file)
            target_dir = Path() / current_file.parent / prefs['move file']
            target_file = Path() / target_dir / current_file.name

            if not Path.exists(target_dir):
                Path(target_dir).mkdir()

        elif action == 'delete':
            dialog = message_dialog.MessageDialog(
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
            dialog.set_text(f'Trash Selected File: "{Path(current_file).name}"?')
            result = dialog.run()
            if result != Gtk.ResponseType.OK:
                return None

        if self.filehandler.get_archive_type() is not None:
            next_opened = self.filehandler.open_next_archive()
            if not next_opened:
                next_opened = self.filehandler.open_previous_archive()
            if not next_opened:
                self.filehandler.close_file()

            if Path.is_file(current_file):
                file_action()
        else:
            if self.imagehandler.get_number_of_pages() > 1:
                # Open the next/previous file
                if self.imagehandler.get_current_page() >= self.imagehandler.get_number_of_pages():
                    self.flip_page(-1)
                else:
                    self.flip_page(+1)
                # Move the desired file
                if Path.is_file(current_file):
                    file_action()

                # Refresh the directory
                self.filehandler.refresh_file()
            else:
                self.filehandler.close_file()
                if Path.is_file(current_file):
                    file_action()

    def minimize(self, *args):
        """Minimizes the MComix window"""
        self.iconify()

    def write_config_files(self):
        preferences.PreferenceManager.write_preferences_file()
        keybindings.keybinding_manager(self).write_keybindings_file()
        bookmark_backend.BookmarksStore.write_bookmarks_file()

    def get_window_geometry(self):
        return self.get_position() + self.get_size()

    def save_window_geometry(self):
        if prefs['window save']:
            (
                prefs['window x'],
                prefs['window y'],
                prefs['window width'],
                prefs['window height'],
            ) = self.get_window_geometry()

    def restore_window_geometry(self):
        if self.get_window_geometry() == (prefs['window x'],
                                          prefs['window y'],
                                          prefs['window width'],
                                          prefs['window height']):
            return False
        self.resize(prefs['window width'], prefs['window height'])
        self.move(prefs['window x'], prefs['window y'])
        return True

    def terminate_program(self, *args):
        """Run clean-up tasks and exit the program"""
        if not self.is_fullscreen:
            self.save_window_geometry()

        self.hide()

        if Gtk.main_level() > 0:
            Gtk.main_quit()

        if prefs['hide all'] and self.__hide_all_forced and self.fullscreen:
            prefs['hide all'] = False

        self.write_config_files()

        self.filehandler.close_file()


def _dummy_layout():
    return layout.FiniteLayout(((1, 1),), (1, 1), (1, 1), 0, False, 0, 0)
