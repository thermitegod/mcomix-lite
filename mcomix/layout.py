# -*- coding: utf-8 -*-

"""Layout"""

from mcomix.hyperrectangles import Box
from mcomix.constants import Constants


class FiniteLayout:  # 2D only
    def __init__(self, content_sizes, viewport_size: tuple, orientation: tuple, spacing: int,
                 wrap_individually: bool, distribution_axis: int, alignment_axis: int):
        """
        Lays out a finite number of Boxes along the first axis.

        :param content_sizes: The sizes of the Boxes to lay out.
        :type content_sizes tuple
        :type content_sizes list
        :param viewport_size: The size of the viewport.
        :param orientation: The orientation to use.
        :param spacing: Number of additional pixels between Boxes.
        :param wrap_individually: True if each content box should get its own
        wrapper box, False if the only wrapper box should be the union of all
        content boxes.
        :param distribution_axis: the axis along which the Boxes are distributed.
        :param alignment_axis: the axis to center
        """

        super().__init__()

        self.__viewport_box = None
        self.__dirty_current_index = None
        self.__orientation = None

        self.__current_index = -1
        self.__wrap_individually = wrap_individually
        self._reset(content_sizes, viewport_size, orientation, spacing,
                    wrap_individually, distribution_axis, alignment_axis)

    def set_viewport_position(self, viewport_position: list):
        """
        Moves the viewport to the specified position.

        :param viewport_position: The new viewport position
        """

        self.__viewport_box = self.__viewport_box.set_position(viewport_position)
        self.__dirty_current_index = True

    def scroll_to_predefined(self, destination: tuple, index: int = None):
        """
        Scrolls the viewport to a predefined destination.

        :param destination: An integer representing a predefined destination.
        Either 1 (towards the greatest possible values in this dimension),
        -1 (towards the smallest value in this dimension), 0 (keep position),
        SCROLL_TO_CENTER (scroll to the center of the content in this
        dimension), SCROLL_TO_START (scroll to where the content starts in this
        dimension) or SCROLL_TO_END (scroll to where the content ends in this
        dimension).
        :param index: The index of the Box the scrolling is related to, None to
        use the index of the current Box, or UNION_INDEX to use the union box
        instead. Note that the current implementation always uses the union box
        if self.wrap_individually is False
        """

        if index is None:
            index = self.get_current_index()
        if not self.__wrap_individually:
            index = Constants.INDEX['UNION']
        if index == Constants.INDEX['UNION']:
            current_box = self.__union_box
        else:
            if index == Constants.INDEX['LAST']:
                index = len(self.__content_boxes) - 1
            current_box = self.__wrapper_boxes[index]
        self.set_viewport_position(self._scroll_to_predefined(
            current_box, self.__viewport_box, self.__orientation, destination))

    @staticmethod
    def _scroll_to_predefined(content_box, viewport_box, orientation: tuple, destination: tuple):
        """
        Returns a new viewport position when scrolling towards a
        predefined destination. Note that all params are lists of integers
        where each index corresponds to one dimension.

        :param content_box: The Box of the content to display.
        :param viewport_box: The viewport Box we are looking through.
        :param orientation: The orientation which shows where "forward"
        points to. Either 1 (towards larger values in this dimension when
        reading) or -1 (towards smaller values in this dimension when reading).
        :param destination: An integer representing a predefined destination.
        Either 1 (towards the greatest possible values in this dimension),
        -1 (towards the smallest value in this dimension), 0 (keep position),
        SCROLL_TO_CENTER (scroll to the center of the content in this
        dimension), SCROLL_TO_START (scroll to where the content starts in this
        dimension) or SCROLL_TO_END (scroll to where the content ends in this dimension).
        :returns: A new viewport position as specified above
        """

        content_position = content_box.get_position()
        content_size = content_box.get_size()
        viewport_size = viewport_box.get_size()
        result = list(viewport_box.get_position())
        for idx, item in enumerate(content_size):
            o = orientation[idx]
            d = destination[idx]

            if not d:
                continue
            elif d < Constants.SCROLL_TO['END'] or d > 1:
                raise ValueError(f'invalid destination {d} at index {i}')
            elif d == Constants.SCROLL_TO['END']:
                d = o
            elif d == Constants.SCROLL_TO['START']:
                d = -o

            c = content_size[idx]
            v = viewport_size[idx]
            invisible_size = c - v

            if d == Constants.SCROLL_TO['CENTER']:
                offset = Box.box_to_center_offset_1d(invisible_size, o)
            else:
                if d == 1:
                    offset = invisible_size
                else:
                    # if d == -1
                    offset = 0

            result[idx] = content_position[idx] + offset

        return result

    def get_content_boxes(self):
        """
        Returns the Boxes as they are arranged in this layout.

        :returns: The Boxes as they are arranged in this layout
        """

        return self.__content_boxes

    def get_union_box(self):
        """
        Returns the union Box for this layout.

        :return: The union Box for this layout
        """

        return self.__union_box

    def get_current_index(self):
        """
        Returns the index of the Box that is said to be the current Box.

        :returns: The index of the Box that is said to be the current Box
        """

        if self.__dirty_current_index:
            self.__current_index = self.__viewport_box.current_box_index(self.__orientation, self.__content_boxes)
            self.__dirty_current_index = False
        return self.__current_index

    def get_viewport_box(self):
        """
        Returns the current viewport Box.

        :returns: The current viewport Box
        """

        return self.__viewport_box

    def set_orientation(self, orientation: tuple):
        self.__orientation = orientation

    def _reset(self, content_sizes, viewport_size: tuple, orientation: tuple, spacing: int,
               wrap_individually: bool, distribution_axis: int, alignment_axis: int):
        # reverse order if necessary
        if orientation[distribution_axis] == -1:
            content_sizes = tuple(reversed(content_sizes))
        temp_cb_list = tuple(map(Box, content_sizes))
        # align to center
        temp_cb_list = Box.align_center(temp_cb_list, alignment_axis, 0, orientation[alignment_axis])
        # distribute
        temp_cb_list = Box.distribute(temp_cb_list, distribution_axis, 0, spacing)
        if wrap_individually:
            temp_wb_list, temp_bb = FiniteLayout._wrap_individually(temp_cb_list, viewport_size, orientation)
        else:
            temp_wb_list, temp_bb = FiniteLayout._wrap_union(temp_cb_list, viewport_size, orientation)
        # move to global origin
        bbp = temp_bb.get_position()
        for idx, item in enumerate(temp_cb_list):
            temp_cb_list[idx] = temp_cb_list[idx].translate_opposite(bbp)
        for idx, item in enumerate(temp_wb_list):
            temp_wb_list[idx] = temp_wb_list[idx].translate_opposite(bbp)
        temp_bb = temp_bb.translate_opposite(bbp)
        # reverse order again, if necessary
        if orientation[distribution_axis] == -1:
            temp_cb_list = tuple(reversed(temp_cb_list))
            temp_wb_list = tuple(reversed(temp_wb_list))
        # done
        self.__content_boxes = temp_cb_list
        self.__wrapper_boxes = temp_wb_list
        self.__union_box = temp_bb
        self.__viewport_box = Box(viewport_size)
        self.__orientation = orientation
        self.__dirty_current_index = True

    @staticmethod
    def _wrap_individually(temp_cb_list: list, viewport_size: tuple, orientation: tuple):
        # calculate (potentially oversized) wrapper Boxes
        temp_wb_list = [None] * len(temp_cb_list)
        for idx, item in enumerate(temp_cb_list):
            temp_wb_list[idx] = temp_cb_list[idx].wrapper_box(viewport_size, orientation)
        # calculate bounding Box
        temp_bb = Box.bounding_box(temp_wb_list)
        return temp_wb_list, temp_bb

    @staticmethod
    def _wrap_union(temp_cb_list: list, viewport_size: tuple, orientation: tuple):
        # calculate bounding Box
        temp_wb_list = [Box.bounding_box(temp_cb_list).wrapper_box(viewport_size, orientation)]
        return temp_wb_list, temp_wb_list[0]
