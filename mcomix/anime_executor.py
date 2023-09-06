# -*- coding: utf-8 -*-

from typing import Callable

from mcomix.preferences import config


class AnimeFrameExecutor:
    def __init__(self):
        super().__init__()

    def frame_executor(self, animation, function: Callable, args: tuple = None, kwargs: dict = None):
        if function is None:
            # function is not a function, do nothing
            return animation

        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        if not config['ANIMATION_TRANSFORM']:
            # transform disabled, do nothing
            return animation

        try:
            framebuffer = animation.framebuffer
        except AttributeError:
            # animation does not have AnimeFrameBuffer, do nothing
            return animation

        return framebuffer.copy(lambda pb: function(pb, *args, **kwargs)).create_animation()
