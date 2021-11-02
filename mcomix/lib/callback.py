# -*- coding: utf-8 -*-

import threading

from gi.repository import GLib
from loguru import logger


class CallbackList:
    """
    Helper class for implementing callbacks within the main thread.
    Add listeners to method calls with method += callback_function
    """

    __slots__ = ('__callbacks', '__object', '__function')

    def __init__(self, obj, function):
        super().__init__()

        self.__callbacks = []
        self.__object = obj
        self.__function = function

    def __call__(self, *args, **kwargs):
        """
        Runs the wrapped function. After the funtion has finished,
        callbacks are run. Code within the function and the callback is
        always executed in the main thread
        """

        if threading.current_thread().name == 'MainThread':
            # Assume that the Callback object is bound to a class method.
            self.__function(self.__object, *args, **kwargs)
            self.__run_callbacks(*args, **kwargs)
        else:
            # Call this method again in the main thread.
            GLib.idle_add(self.__mainthread_call, (args, kwargs))

    def __iadd__(self, function):
        """Support for 'method += callback_function' syntax"""

        if function not in self.__callbacks:
            self.__callbacks.append(function)

        return self

    def __isub__(self, function):
        """Support for 'method -= callback_function' syntax"""

        if function in self.__callbacks:
            self.__callbacks.remove(function)

        return self

    def __mainthread_call(self, params):
        """
        Helper function to execute code in the main thread.
        This will be called by GLib.idle_add, with <params> being a tuple
        of (args, kwargs)
        """

        self(*params[0], **params[1])
        # Removes this function from the idle queue
        return 0

    def __run_callbacks(self, *args, **kwargs):
        """Executes callback functions"""

        for callback in self.__callbacks:
            try:
                callback(*args, **kwargs)
            except Exception as ex:
                logger.error(f'Callback failed: {callback}')
                logger.error(f'Exception: {ex}')


class Callback:
    """Decorator class for using the CallbackList helper"""

    def __init__(self, function):
        super().__init__()

        # This is the function the Callback is decorating.
        self.__function = function

    def __get__(self, obj, cls):
        """
        This method makes Callback implement the descriptor interface.
        Enables calling bound methods with the correct <self> reference.
        Do not ask me why or how this actually works, I simply do not know
        """

        return CallbackList(obj, self.__function)
