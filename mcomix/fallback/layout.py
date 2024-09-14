# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from mcomix.enums import Scroll

# from mcomix_compiled import Box
from mcomix.fallback.box import Box


class Layout:
    def __init__(self, content_sizes: list[tuple], viewport_size: tuple, orientation: list,
                 distribution_axis: int, alignment_axis: int):
        """
        Lays out a finite number of Boxes along the first axis.

        :param content_sizes: The sizes of the Boxes to lay out.
        :param viewport_size: The size of the viewport.
        :param orientation: The orientation to use.
        :param distribution_axis: the axis along which the Boxes are distributed.
        :param alignment_axis: the axis to center
        """

        super().__init__()

        # reverse order if necessary
        if orientation[distribution_axis] == -1:
            content_sizes = list(reversed(content_sizes))
        self.__content_boxes = list(map(Box, content_sizes))

        # align to center
        self.__content_boxes = Box.align_center(self.__content_boxes, alignment_axis, 0, orientation[alignment_axis])

        # distribute
        self.__content_boxes = Box.distribute(self.__content_boxes, distribution_axis, 0)
        self.__union_box = Box.bounding_box(self.__content_boxes).wrapper_box(viewport_size, orientation)

        # move to global origin
        bbp = self.__union_box.get_position()
        for idx, item in enumerate(self.__content_boxes):
            self.__content_boxes[idx] = self.__content_boxes[idx].translate_opposite(bbp)

        self.__union_box = self.__union_box.translate_opposite(bbp)
        # reverse order again, if necessary
        if orientation[distribution_axis] == -1:
            self.__content_boxes = list(reversed(self.__content_boxes))

        # done
        self.__viewport_box = Box(viewport_size)
        self.__orientation = orientation

    def scroll_to_predefined(self, destination: tuple):
        """
        Returns a new viewport position when scrolling towards a
        predefined destination. Note that all params are lists of integers
        where each index corresponds to one dimension.

        :param destination: An integer representing a predefined destination.
        Either 1 (towards the greatest possible values in this dimension),
        -1 (towards the smallest value in this dimension), 0 (keep position),
        SCROLL_TO_CENTER (scroll to the center of the content in this
        dimension), SCROLL_TO_START (scroll to where the content starts in this
        dimension) or SCROLL_TO_END (scroll to where the content ends in this dimension).
        :returns: A new viewport position as specified above
        """

        content_position = self.__union_box.get_position()
        content_size = self.__union_box.get_size()
        viewport_size = self.__viewport_box.get_size()
        result = list(self.__viewport_box.get_position())
        for idx, item in enumerate(content_size):
            # The orientation which shows where "forward"
            # points to. Either 1 (towards larger values in this dimension when
            # reading) or -1 (towards smaller values in this dimension when reading).
            o = self.__orientation[idx]
            d = destination[idx]

            if not d:
                continue
            elif d < Scroll.END.value or d > 1:
                raise ValueError(f'invalid destination {d} at index {idx}')
            elif d == Scroll.END.value:
                d = o
            elif d == Scroll.START.value:
                d = -o

            c = content_size[idx]
            v = viewport_size[idx]
            invisible_size = c - v

            if d == Scroll.CENTER.value:
                offset = Box.box_to_center_offset_1d(invisible_size, o)
            else:
                if d == 1:
                    offset = invisible_size
                else:  # d == -1
                    offset = 0

            result[idx] = content_position[idx] + offset

        # Move the viewport to the specified position.
        self.__viewport_box = self.__viewport_box.set_position(tuple(result))

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

    def get_viewport_box(self):
        """
        Returns the current viewport Box.

        :returns: The current viewport Box
        """

        return self.__viewport_box

    def set_orientation(self, orientation: list):
        self.__orientation = orientation
