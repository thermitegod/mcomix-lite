# -*- coding: utf-8 -*-

"""thumbbar.py - Thumbnail sidebar for main window"""

from urllib.request import pathname2url

import cairo
from gi.repository import Gdk, GdkPixbuf, Gtk

from mcomix import image_tools, thumbnail_view, tools
from mcomix.preferences import prefs


class ThumbnailSidebar(Gtk.ScrolledWindow):
    """A thumbnail sidebar including scrollbar for the main window"""
    # Thumbnail border width in pixels.
    _BORDER_SIZE = 1

    def __init__(self, window):
        super(ThumbnailSidebar, self).__init__()

        self.__window = window
        #: Thumbnail load status
        self.__loaded = False
        #: Selected row in treeview
        self.__currently_selected_row = 0

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.get_vadjustment().step_increment = 15
        self.get_vadjustment().page_increment = 1
        # Disable stupid overlay scrollbars...
        if hasattr(self.props, 'overlay_scrolling'):
            self.props.overlay_scrolling = False

        # models - contains data
        self.__thumbnail_liststore = Gtk.ListStore(int, GdkPixbuf.Pixbuf, bool)

        # view - responsible for laying out the columns
        self.__treeview = thumbnail_view.ThumbnailTreeView(
                self.__thumbnail_liststore,
                0,  # UID
                1,  # pixbuf
                2,  # status
        )
        self.__treeview.set_headers_visible(False)
        self.__treeview.generate_thumbnail = self._generate_thumbnail
        self.__treeview.set_activate_on_single_click(True)

        self.__treeview.connect_after('drag_begin', self._drag_begin)
        self.__treeview.connect('drag_data_get', self._drag_data_get)
        self.__treeview.connect('row-activated', self._row_activated_event)
        self.__treeview.connect('button_press_event', self._mouse_press_event)

        # enable drag and dropping of images from thumbnail bar to some file
        # manager
        self.__treeview.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
                                                 [('text/uri-list', 0, 0)], Gdk.DragAction.COPY)

        # Page column
        self.__thumbnail_page_treeviewcolumn = Gtk.TreeViewColumn(None)
        self.__treeview.append_column(self.__thumbnail_page_treeviewcolumn)
        self.__text_cellrenderer = Gtk.CellRendererText()
        # Right align page numbers.
        self.__text_cellrenderer.set_property('xalign', 1.0)
        self.__thumbnail_page_treeviewcolumn.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.__thumbnail_page_treeviewcolumn.pack_start(self.__text_cellrenderer, False)
        self.__thumbnail_page_treeviewcolumn.add_attribute(self.__text_cellrenderer, 'text', 0)
        self.__thumbnail_page_treeviewcolumn.set_visible(False)

        # Pixbuf column
        self.__thumbnail_image_treeviewcolumn = Gtk.TreeViewColumn(None)
        self.__treeview.append_column(self.__thumbnail_image_treeviewcolumn)
        self.__pixbuf_cellrenderer = Gtk.CellRendererPixbuf()
        self.__thumbnail_image_treeviewcolumn.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.__thumbnail_image_treeviewcolumn.set_fixed_width(self._pixbuf_size)
        self.__thumbnail_image_treeviewcolumn.pack_start(self.__pixbuf_cellrenderer, True)
        self.__thumbnail_image_treeviewcolumn.add_attribute(self.__pixbuf_cellrenderer, 'pixbuf', 1)

        self.__treeview.set_fixed_height_mode(True)
        self.__treeview.set_can_focus(False)

        self.add(self.__treeview)
        self.change_thumbnail_background_color(prefs['thumb bg color'])
        self.show_all()

        self.__window.page_changed += self._on_page_change
        self.__window.imagehandler.page_available += self._on_page_available

        self.__currently_selected_page = 0

    def toggle_page_numbers_visible(self):
        """Enables or disables page numbers on the thumbnail bar"""
        if visible := prefs['show page numbers on thumbnails']:
            number_of_pages = self.__window.imagehandler.get_number_of_pages()
            number_of_digits = tools.number_of_digits(number_of_pages)
            self.__text_cellrenderer.set_property('width-chars', number_of_digits + 1)
            w = self.__text_cellrenderer.get_preferred_size(self.__treeview)[1].width
            self.__thumbnail_page_treeviewcolumn.set_fixed_width(w)
        self.__thumbnail_page_treeviewcolumn.set_visible(visible)

    def get_width(self):
        """Return the width in pixels of the ThumbnailSidebar"""
        return self.size_request().width

    def show(self, *args):
        """Show the ThumbnailSidebar"""
        self.load_thumbnails()
        super(ThumbnailSidebar, self).show()

    def hide(self):
        """Hide the ThumbnailSidebar"""
        super(ThumbnailSidebar, self).hide()
        self.__treeview.stop_update()

    def clear(self):
        """Clear the ThumbnailSidebar of any loaded thumbnails"""
        self.__loaded = False
        self.__treeview.stop_update()
        self.__thumbnail_liststore.clear()
        self.__currently_selected_page = 0

    def resize(self):
        """Reload the thumbnails with the size specified by in the preferences"""
        self.clear()
        self.__thumbnail_image_treeviewcolumn.set_fixed_width(self._pixbuf_size)
        self.load_thumbnails()

    def change_thumbnail_background_color(self, color):
        """Changes the background color of the thumbnail bar"""
        self.set_thumbnail_background(color)
        # Force a redraw of the widget.
        self.__treeview.queue_draw()

    def set_thumbnail_background(self, color):
        rgba = Gdk.RGBA(*color)
        self.__pixbuf_cellrenderer.set_property('cell-background-rgba', rgba)
        self.__text_cellrenderer.set_property('background-rgba', rgba)
        fg_color = image_tools.text_color_for_background_color(color)
        fg_rgba = Gdk.RGBA(*(fg_color.to_floats() + (1.0,)))
        self.__text_cellrenderer.set_property('foreground-rgba', fg_rgba)

    @property
    def _pixbuf_size(self):
        # Don't forget the extra pixels for the border!
        return prefs['thumbnail size'] + 2 * self._BORDER_SIZE

    def load_thumbnails(self):
        """Load the thumbnails, if it is appropriate to do so"""
        if (not self.__window.filehandler.get_file_loaded() or
                self.__window.imagehandler.get_number_of_pages() == 0 or
                self.__loaded):
            return

        self.toggle_page_numbers_visible()

        # Detach model for performance reasons
        model = self.__treeview.get_model()
        self.__treeview.set_model(None)

        # Create empty preview thumbnails.
        filler = self._get_empty_thumbnail()
        for row in range(self.__window.imagehandler.get_number_of_pages()):
            self.__thumbnail_liststore.append((row + 1, filler, False))

        self.__loaded = True

        # Re-attach model
        self.__treeview.set_model(model)

        # Update current image selection in the thumb bar.
        self._set_selected_row(self.__currently_selected_row)

    def _generate_thumbnail(self, uid):
        """Generate the pixbuf for C{path} at demand"""
        assert isinstance(uid, int)
        page = uid
        if (pixbuf := self.__window.imagehandler.get_thumbnail(page,
                                                               prefs['thumbnail size'],
                                                               prefs['thumbnail size'],
                                                               nowait=True)) is not None:
            pixbuf = image_tools.add_border(pixbuf, self._BORDER_SIZE)

        return pixbuf

    def _set_selected_row(self, row, scroll=True):
        """Set currently selected row.
        If <scroll> is True, the tree is automatically
        scrolled to ensure the selected row is visible"""
        self.__currently_selected_row = row
        self.__treeview.get_selection().select_path(row)
        if self.__loaded and scroll:
            self.__treeview.scroll_to_cell(row, use_align=True, row_align=0.25)

    def _get_selected_row(self):
        """Return the index of the currently selected row"""
        try:
            return self.__treeview.get_selection().get_selected_rows()[1][0][0]

        except IndexError:
            return 0

    def _row_activated_event(self, treeview, path, column):
        """Handle events due to changed thumbnail selection"""
        selected_row = self._get_selected_row()
        self._set_selected_row(selected_row, scroll=False)
        self.__window.set_page(selected_row + 1)

    def _mouse_press_event(self, widget, event):
        if self.__window.was_out_of_focus:
            # if the window was out of focus and the user clicks on
            # the thumbbar then do not select that page because they
            # more than likely have many pages open and are simply trying
            # to give mcomix focus again
            return True
        else:
            return False

    def _drag_data_get(self, treeview, context, selection, *args):
        """Put the URI of the selected file into the SelectionData, so that
        the file can be copied (e.g. to a file manager)"""
        selected = self._get_selected_row()
        path = self.__window.imagehandler.get_path_to_page(selected + 1)
        uri = f'file://localhost{pathname2url(path)}'
        selection.set_uris([uri])

    @staticmethod
    def _drag_begin(treeview, context):
        """We hook up on drag_begin events so that we can set the hotspot
        for the cursor at the top left corner of the thumbnail (so that we
        might actually see where we are dropping!)"""
        path = treeview.get_cursor()[0]
        surface = treeview.create_row_drag_icon(path)
        # Because of course a cairo.Win32Surface does not have
        # get_width/get_height, that would be to easy...
        cr = cairo.Context(surface)
        x1, y1, x2, y2 = cr.clip_extents()
        width, height = x2 - x1, y2 - y1
        pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, width, height)
        Gtk.drag_set_icon_pixbuf(context, pixbuf, -5, -5)

    def _get_empty_thumbnail(self):
        """Create an empty filler pixmap"""
        pixbuf = GdkPixbuf.Pixbuf.new(colorspace=GdkPixbuf.Colorspace.RGB,
                                      has_alpha=True,
                                      bits_per_sample=8,
                                      width=self._pixbuf_size,
                                      height=self._pixbuf_size)

        # Make the pixbuf transparent.
        pixbuf.fill(0)

        return pixbuf

    def _on_page_change(self):
        if (row := self.__window.imagehandler.get_current_page() - 1) == self.__currently_selected_row:
            return
        self._set_selected_row(row)

    def _on_page_available(self, page):
        """Called whenever a new page is ready for display"""
        if self.get_visible():
            self.__treeview.draw_thumbnails_on_screen()
