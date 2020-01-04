# -*- coding: utf-8 -*-

"""Layout"""

from mcomix import box, constants


class FiniteLayout(object):  # 2D only
    def __init__(self, content_sizes, viewport_size, orientation, spacing,
                 wrap_individually, distribution_axis, alignment_axis):
        """Lays out a finite number of Boxes along the first axis.
        @param content_sizes: The sizes of the Boxes to lay out.
        @param viewport_size: The size of the viewport.
        @param orientation: The orientation to use.
        @param spacing: Number of additional pixels between Boxes.
        @param wrap_individually: True if each content box should get its own
        wrapper box, False if the only wrapper box should be the union of all
        content boxes.
        @param distribution_axis: the axis along which the Boxes are distributed.
        @param alignment_axis: the axis to center"""
        self.current_index = -1
        self.wrap_individually = wrap_individually
        self._reset(content_sizes, viewport_size, orientation, spacing,
                    wrap_individually, distribution_axis, alignment_axis)

        self.dirty_current_index = None
        self.orientation = None

    def set_viewport_position(self, viewport_position):
        """Moves the viewport to the specified position.
        @param viewport_position: The new viewport position"""
        self.viewport_box = self.viewport_box.set_position(viewport_position)
        self.dirty_current_index = True

    def scroll_to_predefined(self, destination, index=None):
        """Scrolls the viewport to a predefined destination.
        @param destination: An integer representing a predefined destination.
        Either 1 (towards the greatest possible values in this dimension),
        -1 (towards the smallest value in this dimension), 0 (keep position),
        SCROLL_TO_CENTER (scroll to the center of the content in this
        dimension), SCROLL_TO_START (scroll to where the content starts in this
        dimension) or SCROLL_TO_END (scroll to where the content ends in this
        dimension).
        @param index: The index of the Box the scrolling is related to, None to
        use the index of the current Box, or UNION_INDEX to use the union box
        instead. Note that the current implementation always uses the union box
        if self.wrap_individually is False"""
        if index is None:
            index = self.get_current_index()
        if not self.wrap_individually:
            index = constants.UNION_INDEX
        if index == constants.UNION_INDEX:
            current_box = self.union_box
        else:
            if index == constants.LAST_INDEX:
                index = len(self.content_boxes) - 1
            current_box = self.wrapper_boxes[index]
        self.set_viewport_position(self._scroll_to_predefined(
                current_box, self.viewport_box, self.orientation, destination))

    @staticmethod
    def _scroll_to_predefined(content_box, viewport_box, orientation, destination):
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

    def get_content_boxes(self):
        """Returns the Boxes as they are arranged in this layout.
        @return: The Boxes as they are arranged in this layout"""
        return self.content_boxes

    def get_union_box(self):
        """Returns the union Box for this layout.
        @return: The union Box for this layout"""
        return self.union_box

    def get_current_index(self):
        """Returns the index of the Box that is said to be the current Box.
        @return: The index of the Box that is said to be the current Box"""
        if self.dirty_current_index:
            self.current_index = self.viewport_box.current_box_index(self.orientation, self.content_boxes)
            self.dirty_current_index = False
        return self.current_index

    def get_viewport_box(self):
        """Returns the current viewport Box.
        @return: The current viewport Box"""
        return self.viewport_box

    def set_orientation(self, orientation):
        self.orientation = orientation

    def _reset(self, content_sizes, viewport_size, orientation, spacing,
               wrap_individually, distribution_axis, alignment_axis):
        # reverse order if necessary
        if orientation[distribution_axis] == -1:
            content_sizes = tuple(reversed(content_sizes))
        temp_cb_list = tuple(map(box.Box, content_sizes))
        # align to center
        temp_cb_list = box.Box.align_center(temp_cb_list, alignment_axis, 0, orientation[alignment_axis])
        # distribute
        temp_cb_list = box.Box.distribute(temp_cb_list, distribution_axis, 0, spacing)
        if wrap_individually:
            temp_wb_list, temp_bb = FiniteLayout._wrap_individually(temp_cb_list, viewport_size, orientation)
        else:
            temp_wb_list, temp_bb = FiniteLayout._wrap_union(temp_cb_list, viewport_size, orientation)
        # move to global origin
        bbp = temp_bb.get_position()
        for i in range(len(temp_cb_list)):
            temp_cb_list[i] = temp_cb_list[i].translate_opposite(bbp)
        for i in range(len(temp_wb_list)):
            temp_wb_list[i] = temp_wb_list[i].translate_opposite(bbp)
        temp_bb = temp_bb.translate_opposite(bbp)
        # reverse order again, if necessary
        if orientation[distribution_axis] == -1:
            temp_cb_list = tuple(reversed(temp_cb_list))
            temp_wb_list = tuple(reversed(temp_wb_list))
        # done
        self.content_boxes = temp_cb_list
        self.wrapper_boxes = temp_wb_list
        self.union_box = temp_bb
        self.viewport_box = box.Box(viewport_size)
        self.orientation = orientation
        self.dirty_current_index = True

    @staticmethod
    def _wrap_individually(temp_cb_list, viewport_size, orientation):
        # calculate (potentially oversized) wrapper Boxes
        temp_wb_list = [None] * len(temp_cb_list)
        for i in range(len(temp_cb_list)):
            temp_wb_list[i] = temp_cb_list[i].wrapper_box(viewport_size, orientation)
        # calculate bounding Box
        temp_bb = box.Box.bounding_box(temp_wb_list)
        return temp_wb_list, temp_bb

    @staticmethod
    def _wrap_union(temp_cb_list, viewport_size, orientation):
        # calculate bounding Box
        temp_wb_list = [box.Box.bounding_box(temp_cb_list).wrapper_box(viewport_size, orientation)]
        return temp_wb_list, temp_wb_list[0]
