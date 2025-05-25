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

from gi.repository import GObject, Gdk, Gtk

from mcomix.gui.bookmark_menu_item import Bookmark
from mcomix.preferences import config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.gui.main_window import MainWindow
    from mcomix.bookmark_backend import BookmarkBackend


class BookmarksDialog(Gtk.Dialog):
    """
    BookmarksDialog lets the user remove or rearrange bookmarks
    """

    def __init__(self, window: MainWindow, bookmarks_store: BookmarkBackend):
        super().__init__(title='Edit Bookmarks', destroy_with_parent=True)

        self.__window = window

        self.set_transient_for(window)

        self.add_buttons(Gtk.STOCK_REMOVE, Gtk.ResponseType.REJECT)
        self.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.__bookmarks_store = bookmarks_store

        self.set_resizable(True)
        self.set_default_response(Gtk.ResponseType.CLOSE)
        # scroll area fill to the edge
        self.set_border_width(0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_border_width(0)
        scrolled.set_shadow_type(Gtk.ShadowType.IN)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.vbox.pack_start(scrolled, True, True, 0)

        self.__liststore = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING,
                                         GObject.TYPE_STRING, GObject.TYPE_STRING,
                                         Bookmark)

        pos_sort_name = 0
        pos_sort_page = 1
        pos_sort_path = 2
        pos_sort_date = 3

        # total num of pos_sort_*
        self.__total_pos_sort = 4

        treeview = Gtk.TreeView(model=self.__liststore)
        treeview.set_reorderable(True)
        # search by typing first few letters of name
        treeview.set_search_column(pos_sort_name)
        treeview.set_enable_search(True)
        treeview.set_headers_clickable(True)

        self.__selection = treeview.get_selection()

        scrolled.add(treeview)

        cellrenderer_text = Gtk.CellRendererText()

        name_col = Gtk.TreeViewColumn('Name', cellrenderer_text)
        page_col = Gtk.TreeViewColumn('Pages', cellrenderer_text)
        path_col = Gtk.TreeViewColumn('Path', cellrenderer_text)
        date_col = Gtk.TreeViewColumn('Added', cellrenderer_text)

        treeview.append_column(name_col)
        treeview.append_column(page_col)
        treeview.append_column(path_col)
        treeview.append_column(date_col)

        name_col.set_attributes(cellrenderer_text, text=pos_sort_name)
        page_col.set_attributes(cellrenderer_text, text=pos_sort_page)
        path_col.set_attributes(cellrenderer_text, text=pos_sort_path)
        date_col.set_attributes(cellrenderer_text, text=pos_sort_date)
        name_col.set_expand(True)

        name_col.set_sort_column_id(pos_sort_name)
        page_col.set_sort_column_id(pos_sort_page)
        path_col.set_sort_column_id(pos_sort_path)
        date_col.set_sort_column_id(pos_sort_date)

        name_col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        page_col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        path_col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        date_col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)

        if not config['BOOKMARK_SHOW_PATH']:
            path_col.set_visible(False)

        self.__liststore.set_sort_func(pos_sort_name, self._sort_model, ('bookmark_name', 'bookmark_current_page', 'bookmark_path'))
        self.__liststore.set_sort_func(pos_sort_page, self._sort_model, ('bookmark_total_pages', 'bookmark_current_page', 'bookmark_name'))
        self.__liststore.set_sort_func(pos_sort_date, self._sort_model, ('bookmark_date_added',))

        self.resize(config['BOOKMARK_WIDTH'], config['BOOKMARK_HEIGHT'])

        self.connect('response', self._response)
        self.connect('delete_event', self._close)
        self.connect('configure-event', self._size_changed_cb)

        treeview.connect('key_press_event', self._key_press_event)
        treeview.connect('row_activated', self._bookmark_activated)

        for bookmark in self.__bookmarks_store.get_bookmarks():
            self._add_bookmark(bookmark)

        self.show_all()

    def _add_bookmark(self, bookmark):
        """
        Add the <bookmark> to the dialog
        """

        self.__liststore.prepend(bookmark.to_row())

    def _remove_selected(self):
        """
        Remove the currently selected bookmark from the dialog and from the store
        """

        treeiter = self.__selection.get_selected()[1]
        if treeiter is not None:
            bookmark = self.__liststore.get_value(treeiter, self.__total_pos_sort)
            self.__liststore.remove(treeiter)
            self.__bookmarks_store.remove_bookmark(bookmark)

    def _bookmark_activated(self, treeview, path, *args):
        """
        Open the activated bookmark
        """

        _iter = treeview.get_model().get_iter(path)
        bookmark = treeview.get_model().get_value(_iter, self.__total_pos_sort)

        self._close()

        self.__window.bookmark_backend.open_bookmark(path=bookmark.bookmark_path, current_page=bookmark.bookmark_current_page)

    def _sort_model(self, treemodel, iter1, iter2, user_data):
        """
        Custom sort function to sort to model entries based on the
        BookmarkMenuItem's fields specified in @C{user_data}. This is a list of field names
        """

        bookmark1 = treemodel.get_value(iter1, self.__total_pos_sort)
        bookmark2 = treemodel.get_value(iter2, self.__total_pos_sort)

        for property in user_data:
            result = (lambda a, b: (a > b) - (a < b))(getattr(bookmark1, property),
                                                      getattr(bookmark2, property))
            if result != 0:
                return result

        # If the loop didn't return, both entries are equal.
        return 0

    def _response(self, dialog, response):
        match response:
            case Gtk.ResponseType.CLOSE:
                self._close()
            case Gtk.ResponseType.REJECT:
                self._remove_selected()
            case _:
                self.destroy()

    def _key_press_event(self, dialog, event, *args):
        if event.keyval == Gdk.KEY_Delete:
            self._remove_selected()

    def _size_changed_cb(self, *args):
        config['BOOKMARK_WIDTH'] = self.get_allocation().width
        config['BOOKMARK_HEIGHT'] = self.get_allocation().height

    def _close(self, *args):
        """
        Close the dialog and update the _BookmarkBackend with the new ordering
        """

        ordering = []
        treeiter = self.__liststore.get_iter_first()

        while treeiter is not None:
            bookmark = self.__liststore.get_value(treeiter, self.__total_pos_sort)
            ordering.insert(0, bookmark)
            treeiter = self.__liststore.iter_next(treeiter)

        for bookmark in ordering:
            self.__bookmarks_store.remove_bookmark(bookmark)
            self.__bookmarks_store.add_bookmark(bookmark)

        self.destroy()
