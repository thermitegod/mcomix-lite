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

from loguru import logger

from mcomix.enums import Animation
from mcomix.preferences import config


def rotate_pixbuf(src, rotation: int):
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

def get_fitting_size(src_width: int, src_height: int, width: int, height: int,
                     keep_ratio: bool = True, scale_up: bool = False):
    """
    Return a scaled version of <source_size>
    small enough to fit in <target_size>.
    Both <source_size> and <target_size>
    must be (width, height) tuples.
    If <keep_ratio> is True, aspect ratio is kept.
    If <scale_up> is True, <source_size> is scaled up
    when smaller than <target_size>
    """

    if not scale_up and src_width <= width and src_height <= height:
        width, height = src_width, src_height
    else:
        if keep_ratio:
            if (src_width / width) > (src_height / height):
                height = max(src_height * width // src_width, 1)
            else:
                width = max(src_width * height // src_height, 1)
    return width, height

def frame_executor(animation, function: Callable, args: tuple = None, kwargs: dict = None):
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


def fit_pixbuf_to_rectangle(src, width: int, height: int, rotation: int = 0):
    if is_animation(src):
        return frame_executor(src, fit_pixbuf_to_rectangle, args=(width, height, rotation))
    return fit_in_rectangle(src, width, height, False, True, rotation,)

def fit_in_rectangle(src, width: int, height: int, keep_ratio: bool = True, scale_up: bool = False, rotation: int = 0):
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

    if rotation in (90, 270):
        width, height = height, width

    src_width = src.get_width()
    src_height = src.get_height()

    width, height = get_fitting_size(src_width, src_height, width, height, keep_ratio, scale_up)

    if src.get_has_alpha():
        src = add_alpha_background(src, width, height)
    elif (width, height) != (src_width, src_height):
        src = src.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)

    return rotate_pixbuf(src, rotation)

def add_alpha_background(pixbuf, width: int, height: int):
    if config['CHECKERED_BG_FOR_TRANSPARENT_IMAGES']:
        check_size = config['CHECKERED_BG_SIZE']
        color1 = 0x777777
        color2 = 0x999999
    else:
        check_size = 1024
        color1 = 0xFFFFFF
        color2 = 0xFFFFFF

    return pixbuf.composite_color_simple(width, height, GdkPixbuf.InterpType.BILINEAR, 255, check_size, color1, color2)

def add_border_pixbuf(pixbuf):
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

def is_animation(pixbuf) -> bool:
    return isinstance(pixbuf, GdkPixbuf.PixbufAnimation)

def disable_transform(pixbuf) -> bool:
    if is_animation(pixbuf):
        if not hasattr(pixbuf, 'framebuffer'):
            return True
        if not config['ANIMATION_TRANSFORM']:
            return True
    return False

def static_image(pixbuf):
    """
    Returns a non-animated version of the specified pixbuf
    """

    if is_animation(pixbuf):
        return pixbuf.get_static_image()
    return pixbuf

def set_from_pixbuf(image, pixbuf):
    if is_animation(pixbuf):
        return image.set_from_animation(pixbuf)
    return image.set_from_pixbuf(pixbuf)

def load_pixbuf(path: Path, force_static: bool = False):
    """
    Loads a pixbuf from a given image file
    """

    enable_anime = config['ANIMATION_MODE'] != Animation.DISABLED.value

    if not enable_anime or force_static:
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(path))
        except Exception as ex:
            logger.error(f'Failed to load static image: \'{path}\'')
            logger.debug(f'Exception: {ex}')
            return None

        return pixbuf
    else:
        try:
            pixbuf = GdkPixbuf.PixbufAnimation.new_from_file(str(path))
        except Exception as ex:
            logger.error(f'Failed to load animated image: \'{path}\'')
            logger.debug(f'Exception: {ex}')
            return None

        if pixbuf.is_static_image():
            return pixbuf.get_static_image()

        return pixbuf

def create_thumbnail(path: Path, size: int):
    """
    Returns a thumbnail pixbuf for <path>, transparently handling
    both normal image files and archives. Returns None if thumbnail creation
    failed, or if the thumbnail creation is run asynchrounosly

    :param filepath: Path to the image that the thumbnail is generated from.
    :param size: The max size of any one side for the created thumbnails.
    """

    pixbuf = load_pixbuf(path, force_static=True)
    if pixbuf is None:
        return None

    original_width = pixbuf.get_width()
    original_height = pixbuf.get_height()

    # Calculate the new dimensions while preserving the aspect ratio
    aspect_ratio = original_width / original_height
    if original_width > original_height:
        width = size
        height = int(size / aspect_ratio)
    else:
        height = size
        width = int(size * aspect_ratio)

    pixbuf = fit_pixbuf_to_rectangle(pixbuf, width, height)
    pixbuf = add_border_pixbuf(pixbuf)

    return pixbuf
