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

from pathlib import Path

from typing import Callable

from gi.repository import GdkPixbuf

from mcomix.enums import Animation
from mcomix.preferences import config


class _ImageTools:
    def __init__(self):
        super().__init__()

    def rotate_pixbuf(self, src, rotation: int):
        match rotation:
            case 0:
                return src.rotate_simple(GdkPixbuf.PixbufRotation.NONE)
            case 90:
                return src.rotate_simple(GdkPixbuf.PixbufRotation.CLOCKWISE)
            case 180:
                return src.rotate_simple(GdkPixbuf.PixbufRotation.UPSIDEDOWN)
            case 270:
                return src.rotate_simple(GdkPixbuf.PixbufRotation.COUNTERCLOCKWISE)
            case _:
                raise ValueError(f'unsupported rotation: {rotation}')

    def get_fitting_size(self, source_size: tuple, target_size: tuple, keep_ratio: bool = True, scale_up: bool = False):
        """
        Return a scaled version of <source_size>
        small enough to fit in <target_size>.
        Both <source_size> and <target_size>
        must be (width, height) tuples.
        If <keep_ratio> is True, aspect ratio is kept.
        If <scale_up> is True, <source_size> is scaled up
        when smaller than <target_size>
        """

        width, height = target_size
        src_width, src_height = source_size
        if not scale_up and src_width <= width and src_height <= height:
            width, height = src_width, src_height
        else:
            if keep_ratio:
                if (src_width / width) > (src_height / height):
                    height = max(src_height * width // src_width, 1)
                else:
                    width = max(src_width * height // src_height, 1)
        return width, height

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


    def fit_pixbuf_to_rectangle(self, src, rect: tuple, rotation: int):
        if self.is_animation(src):
            return self.frame_executor(
                src, self.fit_pixbuf_to_rectangle,
                args=(rect, rotation)
            )
        return self.fit_in_rectangle(src, rect[0], rect[1],
                                     rotation=rotation,
                                     keep_ratio=False,
                                     scale_up=True)

    def fit_in_rectangle(self, src, width: int, height: int, keep_ratio: bool = True,
                         scale_up: bool = False, rotation: int = 0, scaling_quality=None):
        """
        Scale (and return) a pixbuf so that it fits in a rectangle with
        dimensions <width> x <height>. A negative <width> or <height>
        means an unbounded dimension - both cannot be negative.

        If <rotation> is 90, 180 or 270 we rotate <src> first so that the
        rotated pixbuf is fitted in the rectangle.

        Unless <scale_up> is True we don't stretch images smaller than the
        given rectangle.

        If <keep_ratio> is True, the image ratio is kept, and the result
        dimensions may be smaller than the target dimensions.

        If <src> has an alpha channel it gets a checkboard background
        """

        rotation %= 360

        # if rotation not in (0, 90, 180, 270):
        #     raise ValueError(f'unsupported rotation: {rotation}')

        if rotation in (90, 270):
            width, height = height, width

        if scaling_quality is None:
            scaling_quality = config['GDK_SCALING_FILTER']

        src_width = src.get_width()
        src_height = src.get_height()

        width, height = self.get_fitting_size((src_width, src_height),
                                              (width, height),
                                              keep_ratio=keep_ratio,
                                              scale_up=scale_up)

        if src.get_has_alpha():
            if (width, height) == (src_width, src_height):
                # Using anything other than nearest interpolation will result in a
                # modified image if no resizing takes place (even if it's opaque).
                scaling_quality = GdkPixbuf.InterpType.NEAREST

            src = self.add_alpha_background(src, width, height, scaling_quality)

        elif (width, height) != (src_width, src_height):
            src = src.scale_simple(width, height, scaling_quality)

        return self.rotate_pixbuf(src, rotation)

    def add_alpha_background(self, pixbuf, width: int, height: int, scaling_quality: int = None):
        if config['CHECKERED_BG_FOR_TRANSPARENT_IMAGES']:
            check_size = config['CHECKERED_BG_SIZE']
            color1 = 0x777777
            color2 = 0x999999
        else:
            check_size = 1024
            color1 = 0xFFFFFF
            color2 = 0xFFFFFF

        if scaling_quality is None:
            scaling_quality = GdkPixbuf.InterpType.NEAREST

        return pixbuf.composite_color_simple(width, height, scaling_quality,
                                             255, check_size, color1, color2)

    def add_border_pixbuf(self, pixbuf):
        """
        Return a pixbuf from <pixbuf> with a black, 1 px border
        """

        width = pixbuf.get_width()
        height = pixbuf.get_height()

        canvas = GdkPixbuf.Pixbuf.new(colorspace=GdkPixbuf.Colorspace.RGB,
                                      has_alpha=True, bits_per_sample=8,
                                      width=width + 2, height=height + 2)
        canvas.fill(0x000000FF)  # black

        pixbuf.copy_area(src_x=0, src_y=0, width=width, height=height,
                         dest_pixbuf=canvas, dest_x=1, dest_y=1)
        return canvas

    def is_animation(self, pixbuf):
        return isinstance(pixbuf, GdkPixbuf.PixbufAnimation)

    def disable_transform(self, pixbuf):
        if self.is_animation(pixbuf):
            if not hasattr(pixbuf, 'framebuffer'):
                return True
            if not config['ANIMATION_TRANSFORM']:
                return True

        return False

    def static_image(self, pixbuf):
        """
        Returns a non-animated version of the specified pixbuf
        """

        if self.is_animation(pixbuf):
            return pixbuf.get_static_image()

        return pixbuf

    def set_from_pixbuf(self, image, pixbuf):
        if self.is_animation(pixbuf):
            return image.set_from_animation(pixbuf)

        return image.set_from_pixbuf(pixbuf)

    def load_pixbuf(self, path: Path):
        """
        Loads a pixbuf from a given image file
        """

        enable_anime = config['ANIMATION_MODE'] != Animation.DISABLED.value

        if not enable_anime:
            return GdkPixbuf.Pixbuf.new_from_file(str(path))

        pixbuf = GdkPixbuf.PixbufAnimation.new_from_file(str(path))
        if pixbuf.is_static_image():
            return pixbuf.get_static_image()
        return pixbuf

    def get_image_size(self, path: Path):
        """
        Return image informations: (width, height)
        """

        pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(path))
        return (pixbuf.get_width(), pixbuf.get_height())

    def get_image_mime(self, path: Path):
        """
        Return image informations: (format)
        """

        pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(path))
        formats = GdkPixbuf.Pixbuf.get_formats()
        for format_info in formats:
            if format_info.is_disabled():
                continue
            if format_info.get_name().lower() == pixbuf.get_file_info().get_mime_type().lower():
                return format_info.get_mime_types()[0]
        return None


ImageTools = _ImageTools()
