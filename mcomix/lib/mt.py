# -*- coding: utf-8 -*-

import sys
from multiprocessing.dummy import Pool
from multiprocessing.pool import ThreadPool as mpThreadPool
from threading import Lock
from typing import Callable

from mcomix.preferences import config


class _NamedPool(mpThreadPool):
    def __init__(self, *args, name: str = None, **kwargs):
        self.__name = name
        super().__init__(*args, **kwargs)

    def Process(self, *args, **kwargs):
        if self.__name:
            kwargs.update(name=self.__name)
        return mpThreadPool.Process(*args, **kwargs)


class _ThreadPool:
    # multiprocessing.dummy.Pool with exc_info in error_callback
    def __init__(self, name: str = None, processes: int = None):
        super().__init__()

        self.__name = name
        self.__processes = processes
        self.__pool = _NamedPool(self.__processes, name=self.__name)
        self.__lock = Lock()  # lock for self
        self.__cblock = Lock()  # lock for callback
        self.__errcblock = Lock()  # lock for error_callback
        self.__closed = False

    def __enter__(self):
        return self

    def __exit__(self, etype, value, tb):
        self.terminate()

    def map_async(self, *args: tuple, **kwargs: dict):
        return self.__pool.map_async(*args, **kwargs)

    def join(self):
        return self.__pool.join()

    @staticmethod
    def _trycall(function: Callable, args: tuple = None, kwargs: dict = None, lock: Lock = None):
        if function is None:
            return

        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        with lock:
            try:
                return function(*args, **kwargs)
            except Exception:
                pass

    def _caller(self, function: Callable, args: tuple, kwargs: dict, callback, error_callback, exc_raise: bool):
        try:
            result = function(*args, **kwargs)
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

    def apply_async(self, function: Callable, args: tuple = None, kwargs: dict = None,
                    callback=None, error_callback=None):
        # run error_callback with ThreadPool.name and exc_info if function failed,
        # callback and error_callback will *not* run in multi thread.
        # other arguments is same as Pool.apply_async
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        return self.__pool.apply_async(
            self._caller, (function, args, kwargs, None, error_callback, True),
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


class _GlobalThreadPool:
    def __init__(self):
        super().__init__()

        self.threadpool = _ThreadPool(name='GlobalThreadPool',
                                      processes=config['MAX_THREADS'])


GlobalThreadPool = _GlobalThreadPool()
