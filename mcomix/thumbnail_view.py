# -*- coding: utf-8 -*-

"""Gtk.IconView subclass for dynamically generated thumbnails"""

import functools
import uuid

from gi.repository import Gtk
from gi.repository import GLib

from mcomix.lib.exceptions import MissingPixbuf
from mcomix.lib.threadpool import GlobalThreadPool, Lock


class ThumbnailViewBase:
    """T
    his class provides shared functionality for Gtk.TreeView and
    Gtk.IconView. Instantiating this class directly is *impossible*,
    as it depends on methods provided by the view classes
    """

    def __init__(self, uid_column: int, pixbuf_column: int, status_column: int):
        """
        Constructs a new ThumbnailView.

        :param uid_column: index of unique identifer column.
        :param pixbuf_column: index of pixbuf column.
        :param status_column: index of status boolean column (True if pixbuf is not temporary filler)
        """

        super().__init__()

        #: Keep track of already generated thumbnails.
        self.__uid_column = uid_column
        self.__pixbuf_column = pixbuf_column
        self.__status_column = status_column

        #: Worker thread
        self.__threadpool = GlobalThreadPool.threadpool
        self.__lock = Lock()
        self.__done = set()
        self.__taskid = 0

    def stop_update(self):
        """
        Stops generation of pixbufs
        """

        with self.__lock:
            self.__taskid = 0
            self.__done.clear()

    def draw_thumbnails_on_screen(self, *args):
        """
        Prepares valid thumbnails for currently displayed icons.
        This method is supposed to be called from the expose-event callback function
        """

        # 'draw' event called too frequently
        if not self.__lock.acquire(blocking=False):
            return
        try:
            visible = self.get_visible_range()
            if not visible:
                # No valid paths available
                return

            start = visible[0][0]
            end = visible[1][0]

            # Currently invisible icons are always cached
            # only after the visible icons completed.
            mid = (start + end) // 2 + 1
            harf = end - start + 1  # twice of current visible length
            required = set(range(mid - harf, mid + harf))

            taskid = self.__taskid
            if not taskid:
                taskid = uuid.uuid4().int

            model = self.get_model()
            required &= set(range(len(model)))  # filter invalid paths.
            for path in required:
                _iter = model.get_iter(path)
                uid, generated = model.get(_iter, self.__uid_column, self.__status_column)
                # Do not queue again if thumbnail was already created.
                if generated:
                    continue
                if uid in self.__done:
                    continue
                self.__taskid = taskid
                self.__done.add(uid)
                self.__threadpool.apply_async(
                    self._pixbuf_worker, args=(uid, _iter, model),
                    callback=functools.partial(self._pixbuf_finished, taskid=taskid))
        finally:
            self.__lock.release()

    def _pixbuf_worker(self, uid: int, _iter, model):
        """
        Run by a worker thread to generate the thumbnail for a path
        """

        pixbuf = self.generate_thumbnail(uid)
        if pixbuf is None:
            self.__done.discard(uid)
            raise MissingPixbuf
        return _iter, pixbuf, model

    def _pixbuf_finished(self, params: tuple, taskid: int = -1):
        """
        Executed when a pixbuf was created, to actually insert the pixbuf
        into the view store. C{params} is a tuple containing (index, pixbuf, model)
        """

        with self.__lock:
            if self.__taskid != taskid:
                return
            _iter, pixbuf, model = params
            GLib.idle_add(model.set, _iter, self.__status_column, True, self.__pixbuf_column, pixbuf)


class ThumbnailTreeView(Gtk.TreeView, ThumbnailViewBase):
    def __init__(self, model, uid_column: int, pixbuf_column: int, status_column: int):
        super().__init__(model=model)

        ThumbnailViewBase.__init__(self, uid_column, pixbuf_column, status_column)

        # Connect events
        self.connect('draw', self.draw_thumbnails_on_screen)

    def get_visible_range(self):
        return Gtk.TreeView.get_visible_range(self)
