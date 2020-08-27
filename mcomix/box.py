# -*- coding: utf-8 -*-

"""Hyperrectangles"""

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
            self.__position = (0,) * len(position)
            self.__size = tuple(position)
        else:
            self.__position = tuple(position)
            self.__size = tuple(size)
        if len(self.__position) != len(self.__size):
            raise ValueError(f'different dimensions: {str(len(self.__position))} != {str(len(self.__size))}')

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

    def set_position(self, position: list):
        """
        Returns a new Box that has the same size as this Box and the specified position.

        :return: A new Box as specified above
        """

        return Box(position, self.get_size())

    def set_size(self, size):
        """
        Returns a new Box that has the same position as this Box and the specified size

        :return: A new Box as specified above
        """

        return Box(self.get_position(), size)

    def distance_point_squared(self, point):
        """
        Returns the square of the Euclidean distance between this Box and a
        point. If the point lies within the Box, this Box is said to have a
        distance of zero. Otherwise, the square of the Euclidean distance
        between point and the closest point of the Box is returned.

        :param point: The point of interest.
        :returns: The distance between the point and the Box as specified above
        """

        result = 0
        for idx, item in enumerate(point):
            p = point[idx]
            bs = self.__position[idx]
            be = self.__size[idx] + bs
            if p < bs:
                r = bs - p
            elif p >= be:
                r = p - be + 1
            else:
                continue
            result += r * r
        return result

    def translate_opposite(self, delta: tuple):
        """
        Returns a new Box that has the same size as this Box and a
        oppositely translated position as specified by delta.

        :param delta: The distance to the position of this Box, with opposite direction.
        :return: A new Box as specified above
        """

        return Box(tuple(map(operator.sub, self.get_position(), delta)), self.get_size())

    @staticmethod
    def closest_boxes(point, boxes: list, orientation=None):
        """
        Returns the indices of the Boxes that are closest to the specified
        point. First, the Euclidean distance between point and the closest point
        of the respective Box is used to determine which of these Boxes are the
        closest ones. If two Boxes have the same distance, the Box that is
        closer to the origin as defined by orientation is said to have a shorter
        distance.

        :param point: The point of interest.
        :param boxes: A list of Boxes.
        :param orientation: The orientation which shows where "forward" points
        to. Either 1 (towards larger values in this dimension when reading) or
        -1 (towards smaller values in this dimension when reading). If
        orientation is set to None, it will be ignored.
        :returns: The indices of the closest Boxes as specified above
        """

        result = []
        mindist = -1
        for idx, item in enumerate(boxes):
            # 0 --> keep
            # 1 --> append
            # 2 --> replace
            keep_append_replace = 0
            b = boxes[idx]
            dist = b.distance_point_squared(point)
            if (result == []) or (dist < mindist):
                keep_append_replace = 2
            elif dist == mindist:
                if orientation is not None:
                    # Take orientation into account.
                    # If result is small, a simple iteration shouldn't be a
                    # performance issue.
                    for ridx, ritem in enumerate(result):
                        c = Box._compare_distance_to_origin(b, boxes[result[ridx]], orientation)
                        if c < 0:
                            keep_append_replace = 2
                            break
                        if not c:
                            keep_append_replace = 1
                else:
                    keep_append_replace = 1

            if keep_append_replace == 1:
                result.append(idx)
            if keep_append_replace == 2:
                mindist = dist
                result = [idx]
        return result

    @staticmethod
    def _compare_distance_to_origin(box1, box2, orientation):
        """
        Returns an integer that is less than, equal to or greater than zero
        if the distance between box1 and the origin is less than, equal to or
        greater than the distance between box2 and the origin, respectively.
        The origin is implied by orientation.

        :param box1: The first Box.
        :param box2: The second Box.
        :param orientation: The orientation which shows where "forward" points
        to. Either 1 (towards larger values in this dimension when reading) or
        -1 (towards smaller values in this dimension when reading).
        :returns: An integer as specified above
        """

        for idx, item in enumerate(orientation):
            o = orientation[idx]
            if not o:
                continue
            box1edge = box1.get_position()[idx]
            box2edge = box2.get_position()[idx]
            if o < 0:
                box1edge = box1.get_size()[idx] - box1edge
                box2edge = box2.get_size()[idx] - box2edge
            if (d := box1edge - box2edge) != 0:
                return d
        return 0

    def get_center(self, orientation):
        """
        Returns the center of this Box. If the exact value is not equal to
        an integer, the integer that is closer to the origin (as implied by
        orientation) is chosen.

        :param orientation: The orientation which shows where "forward" points
        to. Either 1 (towards larger values in this dimension when reading) or
        -1 (towards smaller values in this dimension when reading).
        :return The center of this Box as specified above
        """

        result = [0] * len(orientation)
        bp = self.get_position()
        bs = self.get_size()
        for idx, item in enumerate(orientation):
            result[idx] = Box.box_to_center_offset_1d(bs[idx] - 1, orientation[idx]) + bp[idx]
        return result

    @staticmethod
    def box_to_center_offset_1d(box_size_delta: int, orientation: int):
        if orientation == -1:
            box_size_delta += 1
        return box_size_delta >> 1

    def current_box_index(self, orientation, boxes):
        """
        Calculates the index of the Box that is closest to the center of this Box.

        :param orientation: The orientation to use.
        :param boxes: The Boxes to examine.
        :returns: The index as specified above
        """

        return Box.closest_boxes(self.get_center(orientation), boxes, orientation)[0]

    @staticmethod
    def align_center(boxes: tuple, axis: int, fix: int, orientation: int):
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
        if (cs := center_box.get_size()[axis]) % 2 != 0:
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
    def distribute(boxes: list, axis: int, fix: int, spacing: int = 0):
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

    def wrapper_box(self, viewport_size: tuple, orientation: tuple):
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
        return Box(mins, tuple(map(operator.sub, maxes, mins)))
