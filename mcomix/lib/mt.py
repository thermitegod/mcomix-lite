# -*- coding: utf-8 -*-

import sys

from multiprocessing.dummy import Pool
from multiprocessing.pool import ThreadPool as mpThreadPool
from threading import Lock


class NamedPool(mpThreadPool):
    def __init__(self, *args, name: str = None, **kwargs):

        self.__name = name
        super().__init__(*args, **kwargs)

    def Process(self, *args, **kwargs):
        if self.__name:
            kwargs.update(name=self.__name)
        return mpThreadPool.Process(*args, **kwargs)


class ThreadPool:
    # multiprocessing.dummy.Pool with exc_info in error_callback
    def __init__(self, name: str = None, processes: int = None):
        super().__init__()

        self.__processes = processes
        self.__pool = NamedPool(self.__processes, name=name)
        self.__lock = Lock()  # lock for self
        self.__cblock = Lock()  # lock for callback
        self.__errcblock = Lock()  # lock for error_callback
        self.__closed = False

        self.__name = name

    def apply(self, *args, **kwargs):
        return self.__pool.apply(*args, **kwargs)

    def map(self, *args, **kwargs):
        return self.__pool.map(*args, **kwargs)

    def map_async(self, *args, **kwargs):
        return self.__pool.map_async(*args, **kwargs)

    def imap(self, *args, **kwargs):
        return self.__pool.imap(*args, **kwargs)

    def imap_unordered(self, *args, **kwargs):
        return self.__pool.imap_unordered(*args, **kwargs)

    def starmap(self, *args, **kwargs):
        return self.__pool.starmap(*args, **kwargs)

    def starmap_async(self, *args, **kwargs):
        return self.__pool.starmap_async(*args, **kwargs)

    def join(self):
        return self.__pool.join()

    @staticmethod
    def _uiter(iterable):
        buf = []
        for item in iterable:
            if item in buf:
                continue
            yield item
            buf.append(item)
        buf.clear()

    @staticmethod
    def _trycall(func, args=(), kwargs=None, lock=None):
        if kwargs is None:
            kwargs = {}
        if not callable(func):
            return
        with lock:
            try:
                return func(*args, **kwargs)
            except Exception:
                pass

    def _caller(self, func, args, kwargs, callback, error_callback, exc_raise):
        try:
            result = func(*args, **kwargs)
        except Exception:
            etype, value, tb = sys.exc_info()
            self._trycall(error_callback, args=(self.__name, etype, value, tb),
                          lock=self.__errcblock)
            if exc_raise:
                raise etype(value)
        else:
            self._trycall(callback, args=(result,),
                          lock=self.__cblock)
            return result

    def apply_async(self, func, args=(), kwargs=None,
                    callback=None, error_callback=None):
        # run error_callback with ThreadPool.name and exc_info if func failed,
        # callback and error_callback will *not* run in multi thread.
        # other arguments is same as Pool.apply_async
        if kwargs is None:
            kwargs = {}
        return self.__pool.apply_async(
                self._caller, (func, args, kwargs, None, error_callback, True),
                callback=callback)

    def cbmap(self, func, iterable, chunksize=None,
              callback=None, error_callback=None, block=False):
        # shortcut of:
        #
        # for item in iterable:
        #     apply_async(func,args=(items,),kwargs={},
        #                 callback=callback,error_callback=error_callback)
        #
        # always return None
        # block if block set to True
        (self.starmap if block else self.starmap_async)(
                self._caller,
                ((func, (item,), {}, callback, error_callback, not block)
                 for item in iterable),
                chunksize=chunksize)

    def ucbmap(self, func, iterable, chunksize=None,
               callback=None, error_callback=None, block=False):
        # unique version of ThreadPool.cbmap
        return self.cbmap(func, self._uiter(iterable), chunksize,
                          callback, error_callback, block)

    def close(self):
        # same as Pool.close
        self.__closed = True
        return self.__pool.close()

    def terminate(self):
        # same as Pool.terminate
        self.__closed = True
        return self.__pool.terminate()

    def renew(self):
        # terminate all process and start a new clean pool
        with self.__lock:
            self.terminate()
            self.__pool = Pool(self.__processes)
            self.__closed = False

    @property
    def closed(self):
        # True if ThreadPool closed
        return self.__closed

    def __enter__(self):
        return self

    def __exit__(self, etype, value, tb):
        self.terminate()
