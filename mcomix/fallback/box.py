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

import operator


class Box:
    def __init__(self, position, size=None):
        """
        A Box is immutable and always axis-aligned.
        Each component of size should be positive (i.e. non-zero).
        Both position and size must have equal number of dimensions.
        If there is only one argument, it must be the size. In this case, the
        position is set to origin (i.e. all coordinates are 0) by definition.

        :param position: The position of this Box.
        :param size: The size of this Box
        """

        super().__init__()

        if size is None:
            self.__position = [0, 0]
            self.__size = list(position)
        else:
            self.__position = list(position)
            self.__size = list(size)
        if len(self.__position) != len(self.__size):
            raise ValueError(f'different dimensions: {len(self.__position)} != {len(self.__size)}')

    def __str__(self):
        """
        Returns a string representation of this Box

        :returns: a string representation of this Box
        """

        return f'{{{str(self.get_position())}:{str(self.get_size())}}}'

    def __eq__(self, other):
        """
        Two Boxes are said to be equal if and only if the number of
        dimensions, the positions and the sizes of the two Boxes are equal, respectively
        """

        return (self.get_position() == other.get_position()) and (self.get_size() == other.get_size())

    def __len__(self):
        """
        Returns the number of dimensions of this Box

        :returns: the number of dimensions of this Box
        """

        return len(self.__position)

    def get_size(self):
        """
        Returns the size of this Box

        :return: The size of this Box
        """

        return self.__size

    def get_position(self):
        """
        Returns the position of this Box

        :return: The position of this Box
        """

        return self.__position

    def set_position(self, position: list[int]):
        """
        Returns a new Box that has the same size as this Box and the specified position.

        :return: A new Box as specified above
        """

        return Box(position, self.get_size())

    def translate_opposite(self, delta: list[int]):
        """
        Returns a new Box that has the same size as this Box and a
        oppositely translated position as specified by delta.

        :param delta: The distance to the position of this Box, with opposite direction.
        :return: A new Box as specified above
        """

        return Box(list(map(operator.sub, self.get_position(), delta)), self.get_size())

    @staticmethod
    def box_to_center_offset_1d(box_size_delta: int, orientation: int):
        if orientation == -1:
            box_size_delta += 1
        return box_size_delta >> 1

    @staticmethod
    def align_center(boxes: list, axis: int, fix: int, orientation: int):
        """
        Aligns Boxes so that the center of each Box appears on the same line.

        :param boxes: boxes
        :param axis: the axis to center.
        :param fix: the index of the Box that should not move.
        :param orientation: The orientation to use.
        :returns: A list of new Boxes with accordingly translated positions
        """

        if not boxes:
            return []
        center_box = boxes[fix]
        cs = center_box.get_size()[axis]
        if cs % 2 != 0:
            cs += 1
        cp = center_box.get_position()[axis]
        result = []
        for b in boxes:
            s = b.get_size()
            p = list(b.get_position())
            p[axis] = cp + Box.box_to_center_offset_1d(cs - s[axis], orientation)
            result.append(Box(p, s))
        return result

    @staticmethod
    def distribute(boxes: list, axis: int, fix: int, spacing: int = 2):
        """
        Ensures that the Boxes do not overlap. For this purpose, the Boxes
        are distributed according to the index of the respective Box.

        :param boxes: boxes
        :param axis: the axis along which the Boxes are distributed.
        :param fix: the index of the Box that should not move.
        :param spacing: the number of additional pixels between Boxes.
        :returns: A new list with new Boxes that are accordingly translated
        """

        if not boxes:
            return []
        result = [None] * len(boxes)
        initial_sum = boxes[fix].get_position()[axis]
        partial_sum = initial_sum
        for bi in range(fix, len(boxes)):
            b = boxes[bi]
            s = b.get_size()
            p = list(b.get_position())
            p[axis] = partial_sum
            result[bi] = Box(p, s)
            partial_sum += s[axis] + spacing
        partial_sum = initial_sum
        for bi in range(fix - 1, -1, -1):
            b = boxes[bi]
            s = b.get_size()
            p = list(b.get_position())
            partial_sum -= s[axis] + spacing
            p[axis] = partial_sum
            result[bi] = Box(p, s)

        return result

    def wrapper_box(self, viewport_size: list, orientation: list):
        """
        Returns a Box that covers the same area that is covered by a
        scrollable viewport showing this Box.

        :param viewport_size: The size of the viewport.
        :param orientation: The orientation to use.
        :returns: A Box as specified above
        """

        size = self.get_size()
        position = self.get_position()
        result_size = [0] * len(size)
        result_position = [0] * len(size)
        for idx, item in enumerate(size):
            c = size[idx]
            v = viewport_size[idx]
            result_size[idx] = max(c, v)
            result_position[idx] = Box.box_to_center_offset_1d(c - result_size[idx], orientation[idx]) + position[idx]
        return Box(result_position, result_size)

    @staticmethod
    def bounding_box(boxes: list):
        """
        Returns the union of all specified Boxes (that is, the smallest Box
        that contains all specified Boxes).

        :param boxes: The Boxes to calculate the union from.
        :returns: A Box as specified above
        """

        if not boxes:
            return Box((), ())
        mins = [None] * len(boxes[0].get_size())
        maxes = [None] * len(mins)
        for b in boxes:
            s = b.get_size()
            p = b.get_position()
            for idx, item in enumerate(mins):
                if (mins[idx] is None) or (p[idx] < mins[idx]):
                    mins[idx] = p[idx]
                ps = p[idx] + s[idx]
                if (maxes[idx] is None) or (ps > maxes[idx]):
                    maxes[idx] = ps
        return Box(mins, list(map(operator.sub, maxes, mins)))
