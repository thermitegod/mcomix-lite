# -*- coding: utf-8 -*-

from mcomix import box, constants


class Scrolling(object):
    @staticmethod
    def scroll_to_predefined(content_box, viewport_box, orientation, destination):
        """Returns a new viewport position when scrolling towards a
        predefined destination. Note that all params are lists of integers
        where each index corresponds to one dimension.
        @param content_box: The Box of the content to display.
        @param viewport_box: The viewport Box we are looking through.
        @param orientation: The orientation which shows where "forward"
        points to. Either 1 (towards larger values in this dimension when
        reading) or -1 (towards smaller values in this dimension when reading).
        @param destination: An integer representing a predefined destination.
        Either 1 (towards the greatest possible values in this dimension),
        -1 (towards the smallest value in this dimension), 0 (keep position),
        SCROLL_TO_CENTER (scroll to the center of the content in this
        dimension), SCROLL_TO_START (scroll to where the content starts in this
        dimension) or SCROLL_TO_END (scroll to where the content ends in this dimension).
        @return: A new viewport position as specified above"""
        content_position = content_box.get_position()
        content_size = content_box.get_size()
        viewport_size = viewport_box.get_size()
        result = list(viewport_box.get_position())
        for i in range(len(content_size)):
            o = orientation[i]
            d = destination[i]
            if d == 0:
                continue
            if d < constants.SCROLL_TO_END or d > 1:
                raise ValueError(f'invalid destination {d} at index {i}')
            if d == constants.SCROLL_TO_END:
                d = o
            if d == constants.SCROLL_TO_START:
                d = -o
            c = content_size[i]
            v = viewport_size[i]
            invisible_size = c - v
            result[i] = content_position[i] + (box.Box._box_to_center_offset_1d(invisible_size, o)
                                               if d == constants.SCROLL_TO_CENTER
                                               else invisible_size if d == 1 else 0)  # if d == -1
        return result
