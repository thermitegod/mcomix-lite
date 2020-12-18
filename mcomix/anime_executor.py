# -*- coding: utf-8 -*-

from typing import Callable

from mcomix.preferences import config


class AnimeFrameExecutor:
    def __init__(self):
        super().__init__()

    @staticmethod
    def frame_executor(animation, function: Callable, args: tuple = None, kwargs: dict = None):
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

        # call function on every frame
        anime = AnimeFrameBuffer(n_frames=framebuffer.n_frames, loop=framebuffer.loop)
        for n, frame in enumerate(framebuffer.framelist):
            pixbuf, duration = frame
            anime.add_frame(n, function(pixbuf, *args, **kwargs), duration)
        return anime.create_animation()
