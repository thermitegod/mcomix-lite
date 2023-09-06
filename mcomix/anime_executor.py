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
