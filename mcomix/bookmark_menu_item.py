# -*- coding: utf-8 -*-

"""bookmark_menu_item.py - A signle bookmark item"""

from datetime import datetime

from gi.repository import Gtk


class Bookmark(Gtk.ImageMenuItem):
    """_Bookmark represents one bookmark. It extends the Gtk.ImageMenuItem
    and is thus put directly in the bookmarks menu"""

    def __init__(self, window, file_handler, name, path, page, numpages, archive_type, epoch):
        self.__window = window
        self.__archive_type = archive_type

        self._file_handler = file_handler

        self._name = name
        self._path = path
        self._page = page
        self._numpages = numpages
        self._date_added = datetime.fromtimestamp(epoch)

        super(Bookmark, self).__init__(label=str(self), use_underline=False)

        if self.__archive_type is not None:
            im = Gtk.Image.new_from_stock('mcomix-archive', Gtk.IconSize.MENU)
        else:
            im = Gtk.Image.new_from_stock('mcomix-image', Gtk.IconSize.MENU)

        self.set_image(im)
        self.connect('activate', self.load)

    def __str__(self):
        return f'{self._name}, ({self._page} / {self._numpages})'

    def load(self, *args):
        """Open the file and page the bookmark represents"""
        if self._file_handler.get_base_path() != self._path:
            self._file_handler.open_file(self._path, self._page)
        else:
            self.__window.set_page(self._page)

    def same_path(self, path):
        """Return True if the bookmark is for the file <path>"""
        return path == self._path

    def same_page(self, page):
        """Return True if the bookmark is for the same page"""
        return page == self._page

    def to_row(self):
        """Return a tuple corresponding to one row in the _BookmarkDialog's ListStore"""
        stock = self.get_image().get_stock()
        pixbuf = self.render_icon(*stock)
        page = f'{self._page} / {self._numpages}'
        date = self._date_added.strftime('%x %X')

        return pixbuf, self._name, page, self._path, date, self

    def pack(self):
        """Return a tuple suitable for pickling. The bookmark can be fully
        re-created using the values in the tuple"""
        return self._name, self._path, self._page, self._numpages, self.__archive_type, self._date_added.timestamp()

    def clone(self):
        """Creates a copy of the provided Bookmark menu item. This is necessary
        since one bookmark item cannot be anchored in more than one menu. There are,
        however, at least two: The main menu and the popup menu"""
        return Bookmark(
                self.__window,
                self._file_handler,
                self._name,
                self._path,
                self._page,
                self._numpages,
                self.__archive_type,
                self._date_added.timestamp())

    def __eq__(self, other):
        """Equality comparison for Bookmark items"""
        if isinstance(other, Bookmark):
            return self._path == other._path and self._page == other._page

        return False

    def __hash__(self):
        """Hash for this object"""
        return hash(self._path) | hash(self._page)
