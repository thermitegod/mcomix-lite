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

        self.__name = name
        self.__processes = processes
        self.__pool = NamedPool(self.__processes, name=self.__name)
        self.__lock = Lock()  # lock for self
        self.__cblock = Lock()  # lock for callback
        self.__errcblock = Lock()  # lock for error_callback
        self.__closed = False

    def __enter__(self):
        return self

    def __exit__(self, etype, value, tb):
        self.terminate()

    def map_async(self, *args, **kwargs):
        return self.__pool.map_async(*args, **kwargs)

    def join(self):
        return self.__pool.join()

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
