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

from gi.repository import Gdk, GdkPixbuf, Gtk
from loguru import logger

from mcomix.lib.events import Events, EventType
from mcomix.preferences import config
from mcomix.gui.thumbnail_view import ThumbnailTreeView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.gui.main_window import MainWindow


class ThumbnailSidebar(Gtk.ScrolledWindow):
    """
    A thumbnail sidebar including scrollbar for the main window
    """

    # Thumbnail border width in pixels.
    def __init__(self, window: MainWindow):
        super().__init__()

        self.__window = window

        events = Events()
        events.add_event(EventType.PAGE_AVAILABLE, self._on_page_available)
        events.add_event(EventType.PAGE_CHANGED, self._on_page_change)

        #: Thumbnail load status
        self.__loaded = False
        #: Selected row in treeview
        self.__currently_selected_row = 0

        self.__thumbnail_size = config['THUMBNAIL_SIZE'] + 2  # plus border
        self.__width_padding = self.__thumbnail_size + 10
        self.__empty_thumbnail = self._create_empty_thumbnail()

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        # Disable stupid overlay scrollbars...
        self.set_overlay_scrolling(False)

        # models - contains data
        self.__thumbnail_liststore = Gtk.ListStore(int, GdkPixbuf.Pixbuf, bool)

        # view - responsible for laying out the columns
        self.__treeview = ThumbnailTreeView(
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

        # enable drag and dropping of images from thumbnail bar to some file manager
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
        self.__thumbnail_image_treeviewcolumn.set_fixed_width(self.__width_padding)
        self.__thumbnail_image_treeviewcolumn.pack_start(self.__pixbuf_cellrenderer, True)
        self.__thumbnail_image_treeviewcolumn.add_attribute(self.__pixbuf_cellrenderer, 'pixbuf', 1)

        self.__treeview.set_fixed_height_mode(True)
        self.__treeview.set_can_focus(False)

        self.add(self.__treeview)
        self.show_all()

    def toggle_page_numbers_visible(self):
        """
        Enables or disables page numbers on the thumbnail bar
        """

        if config['SHOW_PAGE_NUMBERS_ON_THUMBNAILS']:
            number_of_pages = len(str(self.__window.image_handler.get_number_of_pages()))
            self.__text_cellrenderer.set_property('width-chars', number_of_pages + 1)
            w = self.__text_cellrenderer.get_preferred_size(self.__treeview)[1].width
            self.__thumbnail_page_treeviewcolumn.set_fixed_width(w)

        self.__thumbnail_page_treeviewcolumn.set_visible(config['SHOW_PAGE_NUMBERS_ON_THUMBNAILS'])

    def get_width(self):
        """
        Return the width in pixels of the ThumbnailSidebar
        """

        return self.size_request().width

    def show(self, *args):
        """
        Show the ThumbnailSidebar
        """

        self.load_thumbnails()

        super().show()

    def hide(self):
        """
        Hide the ThumbnailSidebar
        """

        super().hide()

        self.__treeview.stop_update()

    def clear(self):
        """
        Clear the ThumbnailSidebar of any loaded thumbnails
        """

        self.__loaded = False
        self.__treeview.stop_update()
        self.__thumbnail_liststore.clear()

    def resize(self):
        """
        Reload the thumbnails with the size specified by in the preferences
        """

        self.clear()
        self.__thumbnail_size = config['THUMBNAIL_SIZE'] + 2  # plus border
        self.__width_padding = self.__thumbnail_size + 10
        self.__thumbnail_image_treeviewcolumn.set_fixed_width(self.__width_padding)
        self.load_thumbnails()

    def load_thumbnails(self):
        """
        Load the thumbnails, if it is appropriate to do so
        """

        if (not self.__window.file_handler.is_file_loaded() or
                not self.__window.image_handler.get_number_of_pages() or
                self.__loaded):
            return

        self.toggle_page_numbers_visible()

        # Detach model for performance reasons
        model = self.__treeview.get_model()
        self.__treeview.set_model(None)

        # Create empty preview thumbnails.
        for row in range(self.__window.image_handler.get_number_of_pages()):
            self.__thumbnail_liststore.append((row + 1, self.__empty_thumbnail, False))

        self.__loaded = True

        # Re-attach model
        self.__treeview.set_model(model)

        # Update current image selection in the thumb bar.
        self._set_selected_row(self.__currently_selected_row)

    def _generate_thumbnail(self, uid: int):
        """
        Generate the pixbuf for C{path} at demand
        """

        pixbuf = self.__window.image_handler.get_thumbnail(page=uid, size=config['THUMBNAIL_SIZE'])
        if pixbuf is None:
            return None
        return pixbuf

    def _set_selected_row(self, row: int, scroll: bool = True):
        """
        Set currently selected row.
        If <scroll> is True, the tree is automatically
        scrolled to ensure the selected row is visible
        """

        self.__currently_selected_row = row
        self.__treeview.get_selection().select_path(row)
        if self.__loaded and scroll:
            self.__treeview.scroll_to_cell(row, use_align=True, row_align=0.25)

    def _get_selected_row(self):
        """
        :returns: the index of the currently selected row
        """

        try:
            return self.__treeview.get_selection().get_selected_rows()[1][0][0]
        except IndexError:
            logger.warning('failed to get thumbar index')
            return 0

    def _row_activated_event(self, treeview, path, column):
        """
        Handle events due to changed thumbnail selection
        """

        selected_row = self._get_selected_row()
        self._set_selected_row(selected_row, scroll=False)
        self.__window.set_page(selected_row + 1)

    def _drag_data_get(self, treeview, context, selection, *args):
        """
        Put the URI of the selected file into the SelectionData, so that
        the file can be copied (e.g. to a file manager)
        """

        selected = self._get_selected_row()
        path = self.__window.image_handler.get_path_to_page(selected + 1)
        uri = path.as_uri()
        selection.set_uris([uri])

    def _drag_begin(self, treeview, context):
        """
        We hook up on drag_begin events so that we can set the hotspot
        for the cursor at the top left corner of the thumbnail (so that we
        might actually see where we are dropping!)
        """

        path = treeview.get_cursor()[0]
        surface = treeview.create_row_drag_icon(path)
        pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())
        Gtk.drag_set_icon_pixbuf(context, pixbuf, -5, -5)

    def _create_empty_thumbnail(self):
        """
        Create an empty filler pixmap
        """

        pixbuf = GdkPixbuf.Pixbuf.new(colorspace=GdkPixbuf.Colorspace.RGB,
                                      has_alpha=True,
                                      bits_per_sample=8,
                                      width=self.__thumbnail_size,
                                      height=self.__thumbnail_size)

        # Make the pixbuf transparent.
        pixbuf.fill(0)

        return pixbuf

    def _on_page_change(self):
        row = self.__window.image_handler.get_current_page() - 1
        if row < 0:
            row = 0
        if row == self.__currently_selected_row:
            return
        self._set_selected_row(row)

    def _on_page_available(self, page):
        """
        Called whenever a new page is ready for display
        """

        if self.get_visible():
            self.__treeview.draw_thumbnails_on_screen()
