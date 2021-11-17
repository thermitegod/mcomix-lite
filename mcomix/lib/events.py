# -*- coding: utf-8 -*-

import threading
from enum import Enum, auto
from typing import Callable

from gi.repository import GLib
from loguru import logger

from mcomix.lib.metaclass import SingleInstanceMetaClass


class EventType(Enum):
    BOOKMARK_ADD = auto()
    BOOKMARK_REMOVE = auto()
    DRAW_PAGE = auto()
    FILE_AVAILABLE = auto()
    FILE_CLOSED = auto()
    FILE_OPENED = auto()
    FILE_EXTRACTED = auto()
    FILE_LISTED = auto()
    PAGE_AVAILABLE = auto()
    PAGE_CHANGED = auto()


class Events(metaclass=SingleInstanceMetaClass):
    __slots__ = ('__events', '__run_event')

    def __init__(self) -> None:
        super().__init__()

        self.__run_event = _EventMainthread()

        # knockoff defaultdict(list)
        self.__events = {event: [] for event in EventType}

    def add_event(self, event_type: EventType, function: Callable) -> None:
        """
        Register a function to be run for event_type
        """

        logger.trace(f'Added event: {event_type}')
        self.__events[event_type].append(function)

    def remove_event(self, event_type: EventType, function: Callable) -> None:
        """
        Remove a registered function from an event_type
        """

        logger.trace(f'Removing event: {event_type}')
        self.__events[event_type].remove(function)

    def run_events(self, event_type: EventType, function_kwargs: dict = None) -> None:
        """
        Run all registered functions for event_type
        """

        if function_kwargs is None:
            function_kwargs = {}

        for function in self.__events[event_type]:
            # logger.trace(f'Running event: {event_type}')
            self.__run_event(function, function_kwargs)


class _EventMainthread:
    """
    Helper class for running events within the main thread.
    """

    def __init__(self):
        super().__init__()

    def __call__(self, function: Callable, function_kwargs: dict) -> None:
        """
        Event functions must be executed in the main thread, if they are not run
        in the main thread python can segfault with
        'Unable to access opcode bytes at RIP <MEM ADDR>'
        """

        if threading.current_thread().name == 'MainThread':
            self.__run_event(function, function_kwargs)
        else:
            # Call this method again in the main thread.
            GLib.idle_add(self.__mainthread_call, function, function_kwargs)

    def __mainthread_call(self, function: Callable, function_kwargs: dict) -> int:
        """
        Helper function to execute code in the main thread.
        This will be called by GLib.idle_add
        """

        self(function, function_kwargs)
        # Removes this function from the idle queue
        return 0

    def __run_event(self, function: Callable, function_kwargs: dict) -> None:
        """
        Executes event functions
        """

        try:
            function(**function_kwargs)
        except Exception as ex:
            logger.error(f'Event failed: {function}')
            logger.error(f'Exception: {ex}')
