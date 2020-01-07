# -*- coding: utf-8 -*-

"""Gtk.IconView subclass for dynamically generated thumbnails"""

import functools
import uuid

from gi.repository import Gtk

from mcomix import mt
from mcomix.preferences import prefs


class ThumbnailViewBase:
    """This class provides shared functionality for Gtk.TreeView and
    Gtk.IconView. Instantiating this class directly is *impossible*,
    as it depends on methods provided by the view classes"""

    def __init__(self, uid_column, pixbuf_column, status_column):
        """Constructs a new ThumbnailView.
        @param uid_column: index of unique identifer column.
        @param pixbuf_column: index of pixbuf column.
        @param status_column: index of status boolean column (True if pixbuf is not temporary filler)"""

        #: Keep track of already generated thumbnails.
        self.__uid_column = uid_column
        self.__pixbuf_column = pixbuf_column
        self.__status_column = status_column

        #: Worker thread
        self.__threadpool = mt.ThreadPool(name=self.__class__.__name__,
                                          processes=prefs['max thumbnail threads'] or None)
        self.__lock = mt.Lock()
        self.__done = set()
        self.__taskid = 0

    def generate_thumbnail(self, uid):
        """This function must return the thumbnail for C{uid}"""
        raise NotImplementedError()

    def stop_update(self):
        """Stops generation of pixbufs"""
        with self.__lock:
            self.__taskid = 0
            self.__done.clear()

    def draw_thumbnails_on_screen(self, *args):
        """Prepares valid thumbnails for currently displayed icons.
        This method is supposed to be called from the expose-event callback function"""
        # 'draw' event called too frequently
        if not self.__lock.acquire(blocking=False):
            return
        try:
            if not (taskid := self.__taskid):
                taskid = uuid.uuid4().int

            model = self.get_model()
            for idx, item in set(enumerate(model)):
                iter = model.get_iter(idx)
                uid, generated = model.get(iter, self.__uid_column, self.__status_column)
                # Do not queue again if thumbnail was already created.
                if generated:
                    continue
                if uid in self.__done:
                    continue
                self.__taskid = taskid
                self.__done.add(uid)
                self.__threadpool.apply_async(
                        self._pixbuf_worker, args=(uid, iter, model),
                        callback=functools.partial(self._pixbuf_finished, taskid=taskid))
        finally:
            self.__lock.release()

    def _pixbuf_worker(self, uid, iter, model):
        """Run by a worker thread to generate the thumbnail for a path"""
        pixbuf = self.generate_thumbnail(uid)
        if pixbuf is None:
            self.__done.discard(uid)
            raise Exception('no pixbuf, skip callback.')
        return iter, pixbuf, model

    def _pixbuf_finished(self, params, taskid=-1):
        """Executed when a pixbuf was created, to actually insert the pixbuf
        into the view store. C{params} is a tuple containing (index, pixbuf, model)"""
        with self.__lock:
            if self.__taskid != taskid:
                return
            iter, pixbuf, model = params
            model.set(iter, self.__status_column, True, self.__pixbuf_column, pixbuf)


class ThumbnailTreeView(Gtk.TreeView, ThumbnailViewBase):
    def __init__(self, model, uid_column, pixbuf_column, status_column):
        assert (model.get_flags() & Gtk.TreeModelFlags.ITERS_PERSIST) != 0
        super(ThumbnailTreeView, self).__init__(model=model)
        ThumbnailViewBase.__init__(self, uid_column, pixbuf_column, status_column)

        # Connect events
        self.connect('draw', self.draw_thumbnails_on_screen)

    def get_visible_range(self):
        return Gtk.TreeView.get_visible_range(self)
