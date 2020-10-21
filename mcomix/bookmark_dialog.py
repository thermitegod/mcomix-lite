# -*- coding: utf-8 -*-

"""bookmark_dialog.py - Bookmarks dialog handler"""

from gi.repository import GObject, Gdk, GdkPixbuf, Gtk

from mcomix.bookmark_menu_item import Bookmark
from mcomix.constants import Constants
from mcomix.preferences import config


class BookmarksDialog(Gtk.Dialog):
    """
    BookmarksDialog lets the user remove or rearrange bookmarks
    """

    def __init__(self, window, bookmarks_store):
        super().__init__(title='Edit Bookmarks', destroy_with_parent=True)

        self.__SORT_TYPE = 100
        self.__SORT_NAME = 101
        self.__SORT_PAGE = 102
        self.__SORT_ADDED = 103

        self.set_transient_for(window)

        self.add_buttons(Gtk.STOCK_REMOVE, Constants.RESPONSE_REMOVE, Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.__bookmarks_store = bookmarks_store

        self.set_resizable(True)
        self.set_default_response(Gtk.ResponseType.CLOSE)
        # scroll area fill to the edge (TODO window should not really be a dialog)
        self.set_border_width(0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_border_width(0)
        scrolled.set_shadow_type(Gtk.ShadowType.IN)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.vbox.pack_start(scrolled, True, True, 0)

        self.__liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, GObject.TYPE_STRING, GObject.TYPE_STRING,
                                         GObject.TYPE_STRING, GObject.TYPE_STRING, Bookmark)

        self.__treeview = Gtk.TreeView(model=self.__liststore)
        self.__treeview.set_rules_hint(True)
        self.__treeview.set_reorderable(True)
        # search by typing first few letters of name
        self.__treeview.set_search_column(1)
        self.__treeview.set_enable_search(True)
        self.__treeview.set_headers_clickable(True)
        self._selection = self.__treeview.get_selection()

        scrolled.add(self.__treeview)

        cellrenderer_text = Gtk.CellRendererText()
        cellrenderer_pbuf = Gtk.CellRendererPixbuf()

        self.__icon_col = Gtk.TreeViewColumn('Type', cellrenderer_pbuf)
        self.__name_col = Gtk.TreeViewColumn('Name', cellrenderer_text)
        self.__page_col = Gtk.TreeViewColumn('Pages', cellrenderer_text)
        self.__path_col = Gtk.TreeViewColumn('Location', cellrenderer_text)
        self.__date_add_col = Gtk.TreeViewColumn('Added', cellrenderer_text)

        self.__treeview.append_column(self.__icon_col)
        self.__treeview.append_column(self.__name_col)
        self.__treeview.append_column(self.__page_col)
        self.__treeview.append_column(self.__path_col)
        self.__treeview.append_column(self.__date_add_col)

        self.__icon_col.set_attributes(cellrenderer_pbuf, pixbuf=0)
        self.__name_col.set_attributes(cellrenderer_text, text=1)
        self.__page_col.set_attributes(cellrenderer_text, text=2)
        self.__path_col.set_attributes(cellrenderer_text, text=3)
        self.__date_add_col.set_attributes(cellrenderer_text, text=4)
        self.__name_col.set_expand(True)

        self.__liststore.set_sort_func(self.__SORT_TYPE, self._sort_model, ('_archive_type', '_name', '_page'))
        self.__liststore.set_sort_func(self.__SORT_NAME, self._sort_model, ('_name', '_page', '_path'))
        self.__liststore.set_sort_func(self.__SORT_PAGE, self._sort_model, ('_numpages', '_page', '_name'))
        self.__liststore.set_sort_func(self.__SORT_ADDED, self._sort_model, ('_date_added',))

        self.__icon_col.set_sort_column_id(self.__SORT_TYPE)
        self.__name_col.set_sort_column_id(self.__SORT_NAME)
        self.__page_col.set_sort_column_id(self.__SORT_PAGE)
        self.__path_col.set_sort_column_id(3)
        self.__date_add_col.set_sort_column_id(self.__SORT_ADDED)

        self.__icon_col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.__name_col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.__page_col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.__path_col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.__date_add_col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)

        if not config['BOOKMARK_SHOW_PATH']:
            self.__path_col.set_visible(False)

        self.resize(config['BOOKMARK_WIDTH'], config['BOOKMARK_HEIGHT'])

        self.connect('response', self._response)
        self.connect('delete_event', self._close)

        self.__treeview.connect('key_press_event', self._key_press_event)
        self.__treeview.connect('row_activated', self._bookmark_activated)

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

        treeiter = self._selection.get_selected()[1]
        if treeiter is not None:
            bookmark = self.__liststore.get_value(treeiter, 5)
            self.__liststore.remove(treeiter)
            self.__bookmarks_store.remove_bookmark(bookmark)

    def _bookmark_activated(self, treeview, path, *args):
        """
        Open the activated bookmark
        """

        _iter = treeview.get_model().get_iter(path)
        bookmark = treeview.get_model().get_value(_iter, 5)

        self._close()
        bookmark.load()

    @staticmethod
    def _sort_model(treemodel, iter1, iter2, user_data):
        """
        Custom sort function to sort to model entries based on the
        BookmarkMenuItem's fields specified in @C{user_data}. This is a list of field names
        """

        bookmark1 = treemodel.get_value(iter1, 5)
        bookmark2 = treemodel.get_value(iter2, 5)

        for field in user_data:
            result = (lambda a, b: (a > b) - (a < b))(getattr(bookmark1, field),
                                                      getattr(bookmark2, field))
            if result != 0:
                return result

        # If the loop didn't return, both entries are equal.
        return 0

    def _response(self, dialog, response):
        if response == Gtk.ResponseType.CLOSE:
            self._close()
        elif response == Constants.RESPONSE_REMOVE:
            self._remove_selected()
        else:
            self.destroy()

    def _key_press_event(self, dialog, event, *args):
        if event.keyval == Gdk.KEY_Delete:
            self._remove_selected()

    def _close(self, *args):
        """
        Close the dialog and update the _BookmarksStore with the new ordering
        """

        ordering = []
        treeiter = self.__liststore.get_iter_first()

        while treeiter is not None:
            bookmark = self.__liststore.get_value(treeiter, 5)
            ordering.insert(0, bookmark)
            treeiter = self.__liststore.iter_next(treeiter)

        for bookmark in ordering:
            self.__bookmarks_store.remove_bookmark(bookmark)
            self.__bookmarks_store.add_bookmark(bookmark)

        self.destroy()
