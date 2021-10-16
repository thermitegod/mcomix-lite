# -*- coding: utf-8 -*-

"""Handles zoom and fit of images in the main display area"""

import operator
from functools import reduce

from loguru import logger

from mcomix.preferences import config
from mcomix.enum.zoom_modes import ZoomAxis, ZoomModes


class ZoomModel:
    """
    Handles zoom and fit modes
    """

    def __init__(self):
        super().__init__()

        self.__identity_zoom = 1.0
        self.__identity_zoom_log = 0.0
        self.__user_zoom_log_scale1 = 4.0
        self.__min_user_zoom_log = -20
        self.__max_user_zoom_log = 12

        #: User zoom level.
        self.__user_zoom_log = 0.0

        #: Image fit mode. Determines the base zoom level for an image by
        #: calculating its maximum size.
        self.__fitmode = ZoomModes.MANUAL
        self.__scale_up = False

    def set_fit_mode(self, fitmode: int):
        self.__fitmode = ZoomModes(fitmode)

    def set_scale_up(self, scale_up: bool):
        self.__scale_up = scale_up

    def _set_user_zoom_log(self, zoom_log: float):
        self.__user_zoom_log = min(max(zoom_log, self.__min_user_zoom_log), self.__max_user_zoom_log)

    def zoom_in(self):
        self._set_user_zoom_log(self.__user_zoom_log + 1)

    def zoom_out(self):
        self._set_user_zoom_log(self.__user_zoom_log - 1)

    def reset_user_zoom(self):
        self._set_user_zoom_log(self.__identity_zoom_log)

    def scale(self, t: list, factor: float):
        return [x * factor for x in t]

    def get_zoomed_size(self, image_sizes: list, screen_size: list, distribution_axis: int, do_not_transform: list):
        scale_up = self.__scale_up
        fitted_image_sizes = self._fix_page_sizes(image_sizes, distribution_axis, do_not_transform)
        union_size = self._union_size(fitted_image_sizes, distribution_axis)
        limits = self._calc_limits(union_size, screen_size, self.__fitmode, scale_up)

        prefscale = self._preferred_scale(union_size, limits, distribution_axis)
        preferred_scales = [(self.__identity_zoom if dnt else prefscale) for dnt in do_not_transform]
        prescaled = [tuple(self._scale_image_size(size, scale))
                     for size, scale in zip(fitted_image_sizes, preferred_scales)]
        prescaled_union_size = self._union_size(prescaled, distribution_axis)

        other_preferences = False
        for idx, item in enumerate(limits):
            if idx == distribution_axis:
                continue
            if limits[idx] is not None:
                other_preferences = True
                break

        if limits[distribution_axis] is not None and \
                (prescaled_union_size[distribution_axis] > screen_size[distribution_axis]
                 or not other_preferences):
            distributed_scales = self._scale_distributed(fitted_image_sizes,
                                                         distribution_axis,
                                                         limits[distribution_axis],
                                                         scale_up,
                                                         do_not_transform)
            if other_preferences:
                preferred_scales = map(min, preferred_scales, distributed_scales)
            else:
                preferred_scales = distributed_scales

        if not scale_up:
            preferred_scales = map(lambda x: min(x, self.__identity_zoom), preferred_scales)
        preferred_scales = list(preferred_scales)
        user_scale = 2 ** (self.__user_zoom_log / self.__user_zoom_log_scale1)
        res_scales = [preferred_scales[idx] * (user_scale if not do_not_transform[idx] else self.__identity_zoom)
                      for idx, item in enumerate(preferred_scales)]

        return [tuple(self._scale_image_size(size, scale))
                for size, scale in zip(fitted_image_sizes, res_scales)]

    def _preferred_scale(self, image_size: list, limits: list, distribution_axis: int):
        """
        Returns scale that makes an image of size image_size respect the
        limits imposed by limits. If no proper value can be determined,
        self.__identity_zoom is returned
        """

        min_scale = None
        for idx, item in enumerate(limits):
            if idx == distribution_axis:
                continue
            l = limits[idx]
            if l is None:
                continue
            s = l / image_size[idx]
            if min_scale is None or s < min_scale:
                min_scale = s
        if min_scale is None:
            min_scale = self.__identity_zoom
        return min_scale

    def _calc_limits(self, union_size: list, screen_size: list, fitmode: int, allow_upscaling: bool):
        """
        Returns a list or a tuple with the i-th element set to int x if
        fitmode limits the size at the i-th axis to x, or None if fitmode has no
        preference for this axis
        """

        manual = fitmode == ZoomModes.MANUAL
        if fitmode == ZoomModes.BEST or \
                (manual and allow_upscaling and all(map(operator.lt, union_size, screen_size))):
            return screen_size

        result = [None] * len(screen_size)
        if not manual:
            fixed_size = None

            if fitmode == ZoomModes.SIZE:
                fitmode = ZoomModes(config['FIT_TO_SIZE_MODE'])  # reassigning fitmode
                fixed_size = config['FIT_TO_SIZE_PX']

            if fitmode == ZoomModes.WIDTH:
                axis = ZoomAxis.WIDTH.value
            elif fitmode == ZoomModes.HEIGHT:
                axis = ZoomAxis.HEIGHT.value
            else:
                logger.error('Cannot map fitmode to axis')

            result[axis] = fixed_size if fixed_size is not None else screen_size[axis]

        return result

    def _scale_distributed(self, sizes: list, axis: int, max_size: int,
                           allow_upscaling: bool, do_not_transform: list):
        """
        Calculates scales for a list of boxes that are distributed along a
        given axis (without any gaps). If the resulting scales are applied to
        their respective boxes, their new total size along axis will be as close
        as possible to max_size. The current implementation ensures that equal
        box sizes are mapped to equal scales.
        :param sizes: A list of box sizes.
        :param axis: The axis along which those boxes are distributed.
        :param max_size: The maximum size the scaled boxes may have along axis.
        :param allow_upscaling: True if upscaling is allowed, False otherwise.
        :param do_not_transform: True if the resulting scale must be 1, False
        otherwise.
        :returns: A list of scales where the i-th scale belongs to the i-th box
        size. If sizes is empty, the empty list is returned. If there are more
        boxes than max_size, an approximation is returned where all resulting
        scales will shrink their respective boxes to 1 along axis. In this case,
        the scaled total size might be greater than max_size
        """

        # trivial cases first
        n = len(sizes)
        if not n:
            return []
        if n >= max_size:
            # In this case, only one solution or only an approximation is available.
            # if n > max_size, the result won't fit into max_size.
            return map(lambda x: (1 / x[axis]), sizes)  # FIXME ignores do_not_transform

        total_axis_size = sum(map(lambda x: x[axis], sizes))
        if (total_axis_size <= max_size) and not allow_upscaling:
            # identity
            return [self.__identity_zoom] * n

        # non-trival case
        scale = max_size / total_axis_size  # FIXME initial guess should take unscalable images into account
        scaling_data = [None] * n
        total_axis_size = 0
        # This loop collects some data we need for the actual computations later.
        for i in range(n):
            this_size = sizes[i]

            # Shortcut: If the size cannot be changed, accept the original size.
            if do_not_transform[i]:
                total_axis_size += this_size[axis]
                scaling_data[i] = [self.__identity_zoom, self.__identity_zoom, False, self.__identity_zoom, 0.0]
                continue
            # Initial guess: The current scale works for all tuples.
            ideal = self.scale(this_size, scale)
            ideal_vol = reduce(operator.mul, ideal, 1)
            # Let's use a dummy to compute the actual (rounded) size along axis
            # so we can rescale the rounded tuple with a better local_scale
            # later. This rescaling is necessary to ensure that the sizes in ALL
            # dimensions are monotonically scaled (with respect to local_scale).
            # A nice side effect of this is that it keeps the aspect ratio better.
            dummy_approx = self._round_nonempty([ideal[axis]])[0]
            local_scale = dummy_approx / this_size[axis]
            total_axis_size += dummy_approx
            can_be_downscaled = dummy_approx > 1
            if can_be_downscaled:
                forced_size = dummy_approx - 1
                forced_scale = forced_size / this_size[axis]
                forced_approx = self._scale_image_size(this_size, forced_scale)
                forced_vol_err = (reduce(operator.mul, forced_approx, 1) - ideal_vol) / ideal_vol
            else:
                forced_scale = None
                forced_vol_err = None
            scaling_data[i] = [local_scale, ideal, can_be_downscaled, forced_scale, forced_vol_err]

        # Now we need to find at most total_axis_size - max_size occasions to
        # scale down some tuples so the whole thing would fit into max_size. If
        # we are lucky, there will be no gaps at the end (or at least fewer gaps
        # than we would have if we always rounded down).
        dirty = True  # This flag prevents infinite loops if nothing can be made any smaller.
        while dirty and (total_axis_size > max_size):
            # This algorithm needs O(n*n) time. Let's hope that n is small enough.
            dirty = False
            current_index = 0
            current_min = None
            for i in range(n):
                d = scaling_data[i]
                if not d[2]:
                    # Ignore elements that cannot be made any smaller.
                    continue
                if (current_min is None) or (d[4] < current_min[4]):
                    # We are searching for the tuple where downscaling results
                    # in the smallest relative volume error (compared to the
                    # respective ideal volume).
                    current_min = d
                    current_index = i
            for i in range(current_index, n):
                # We must scale down ALL equal tuples. Otherwise, images that
                # are of equal size might appear to be of different size
                # afterwards. The downside of this approach is that it might
                # introduce more gaps than necessary.
                d = scaling_data[i]
                if (not d[2]) or (d[1] != current_min[1]):
                    continue
                d[0] = d[3]
                d[2] = False  # only once per tuple
                total_axis_size -= 1
                dirty = True
        else:
            # If we are here and total_axis_size < max_size, we could try to
            # upscale some tuples similarily to the other loop (i.e. smallest
            # relative volume error first, equal boxes in conjunction with each
            # other). However, this is not as useful as the other loop, slightly
            # more complicated and it won't do anything if all tuples are equal.
            pass

        return map(lambda d: d[0], scaling_data)

    def _scale_image_size(self, size: list, scale: float):
        return self._round_nonempty(self.scale(size, scale))

    def _round_nonempty(self, t: list):
        result = [0] * len(t)
        for idx, item in enumerate(t):
            x = int(round(t[idx]))
            result[idx] = x if x > 0 else 1
        return result

    def _fix_page_sizes(self, image_sizes: list, distribution_axis: int, do_not_transform: list):
        if len(image_sizes) < 2:
            return image_sizes
        # in double page mode, resize the smaller image to fit the bigger one
        sizes = list(zip(*image_sizes))  # [(x1,x2,...),(y1,y2,...)]
        axis_sizes = sizes[int(not distribution_axis)]  # use axis else of distribution_axis
        max_size = max(axis_sizes)  # max size of pages
        ratios = [(1 if do_not_transform[n] else max_size / s)
                  for n, s in enumerate(axis_sizes)]  # scale ratio of every page if do transform
        return [[int(x * ratios[n]), int(y * ratios[n])]
                for n, (x, y) in enumerate(image_sizes)]  # scale every page

    def _union_size(self, image_sizes: list, distribution_axis: int):
        if not image_sizes:
            return []
        n = len(image_sizes[0])
        union_size = list(map(lambda i: reduce(max, map(lambda x: x[i], image_sizes)), range(n)))
        union_size[distribution_axis] = sum(tuple(map(lambda x: x[distribution_axis], image_sizes)))
        return union_size
