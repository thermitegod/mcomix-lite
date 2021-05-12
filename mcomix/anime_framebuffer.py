# -*- coding: utf-8 -*-

import math
from typing import Callable

from gi.repository import GdkPixbuf

from mcomix.constants import Constants
from mcomix.preferences import config


class AnimeFrameBuffer:
    def __init__(self, n_frames: int, loop: int = 1):
        super().__init__()

        self.__n_frames = n_frames
        self.__width = 0
        self.__height = 0
        if config['ANIMATION_MODE'] == Constants.ANIMATION['INF']:
            self.__loop = 0
        elif config['ANIMATION_MODE'] == Constants.ANIMATION['ONCE']:
            self.__loop = 1
        else:
            self.__loop = 0 if loop > 10 else loop  # loop over 10 is infinitely

        self.__framelist = [None] * n_frames
        self.__duration = 0
        self.__fps = 0

    def add_frame(self, index, pixbuf, duration, background=None):
        if self.__n_frames <= index:
            raise EOFError('index over')
        width = pixbuf.get_width()
        height = pixbuf.get_height()
        if self.__width * self.__height:
            if width != self.__width or height != self.__height:
                raise ValueError('frame with different size')
        else:
            self.__width = width
            self.__height = height
        if config['ANIMATION_BACKGROUND'] and background:
            pixbuf = pixbuf.composite_color_simple(
                width, height, GdkPixbuf.InterpType.NEAREST,
                255, 1024, background, background
            )
        self.__framelist[index] = (pixbuf, duration)
        self.__duration = math.gcd(duration, self.__duration)

    def copy(self, function: Callable[["GdkPixbuf"], "GdkPixbuf"] = None) -> "AnimeFrameBuffer":
        newbuffer = AnimeFrameBuffer(n_frames=self.__n_frames, loop=self.__loop)
        for n, frame in enumerate(self.__framelist):
            pixbuf, duration = frame
            newbuffer.add_frame(index=n, pixbuf=function(pixbuf) if function else pixbuf, duration=duration)
        return newbuffer

    def create_animation(self):
        if not self.__width * self.__height:
            raise ValueError('no frames')
        if not self.__fps:
            if self.__duration:
                self.__fps = 1000 / self.__duration
            else:
                # all duration is 0, set fps to 60
                # TODO: correctly deal with 0 duration
                self.__fps = 60
        anime = GdkPixbuf.PixbufSimpleAnim.new(self.__width, self.__height, self.__fps)
        if self.__loop:
            anime.set_loop(False)
        else:
            anime.set_loop(True)
        for l in range(max(1, self.__loop)):
            for n, frame in enumerate(self.__framelist):
                if not frame:
                    raise OSError('animation corrupted')
                pixbuf, duration = frame
                if not (duration and self.__duration):
                    loop = 1
                else:
                    loop = duration // self.__duration
                for c in range(loop):
                    anime.add_frame(pixbuf)

        anime.framebuffer = self

        return anime
