# -*- coding: utf-8 -*-

"""image_tools.py - Various image manipulations"""

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps, ImageSequence
from gi.repository import GLib, GdkPixbuf
from loguru import logger

from mcomix.anime_executor import AnimeFrameExecutor
from mcomix.anime_framebuffer import AnimeFrameBuffer
from mcomix.constants import Constants
from mcomix.lib.reader import LockedFileIO
from mcomix.preferences import config


class _ImageTools:
    def __init__(self):
        super().__init__()

        # disable PIL DecompressionBombWarning
        Image.MAX_IMAGE_PIXELS = None

        # formats supported by PIL
        Image.init()
        self.__supported_image_exts = [ext for ext in Image.EXTENSION]

    @property
    def supported_image_exts(self):
        return self.__supported_image_exts

    def is_image_file(self, path: Path):
        return path.suffix.lower() in self.__supported_image_exts

    @staticmethod
    def rotate_pixbuf(src, rotation: int):
        if rotation == 0:
            return src
        elif rotation == 90:
            return src.rotate_simple(GdkPixbuf.PixbufRotation.CLOCKWISE)
        elif rotation == 180:
            return src.rotate_simple(GdkPixbuf.PixbufRotation.UPSIDEDOWN)
        elif rotation == 270:
            return src.rotate_simple(GdkPixbuf.PixbufRotation.COUNTERCLOCKWISE)
        else:
            raise ValueError(f'unsupported rotation: {rotation}')

    @staticmethod
    def get_fitting_size(source_size: tuple, target_size: tuple, keep_ratio: bool = True, scale_up: bool = False):
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

    def trans_pixbuf(self, src, flip: bool = False, flop: bool = False):
        if self.is_animation(src):
            return AnimeFrameExecutor.frame_executor(
                src, self.trans_pixbuf,
                kwargs=dict(flip=flip, flop=flop)
            )
        if flip:
            src = src.flip(horizontal=False)
        if flop:
            src = src.flip(horizontal=True)
        return src

    def fit_pixbuf_to_rectangle(self, src, rect: tuple, rotation: int):
        if self.is_animation(src):
            return AnimeFrameExecutor.frame_executor(
                src, self.fit_pixbuf_to_rectangle,
                args=(rect, rotation)
            )
        return self.fit_in_rectangle(src, rect[0], rect[1],
                                     rotation=rotation,
                                     keep_ratio=False,
                                     scale_up=True)

    def fit_in_rectangle(self, src, width: int, height: int, keep_ratio: bool = True,
                         scale_up: bool = False, rotation: int = 0, scaling_quality=None,
                         pil_filter: int = None):
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

        # "Unbounded" really means "bounded to 100000 px" - for simplicity.
        # MComix would probably choke on larger images anyway.
        if width < 0:
            width = 100000
        elif height < 0:
            height = 100000
        width = max(width, 1)
        height = max(height, 1)

        rotation %= 360

        if rotation not in (0, 90, 180, 270):
            raise ValueError(f'unsupported rotation: {rotation}')

        if rotation in (90, 270):
            width, height = height, width

        if scaling_quality is None:
            scaling_quality = config['SCALING_QUALITY']

        if pil_filter is None:
            pil_filter = config['PIL_SCALING_FILTER']

        src_width = src.get_width()
        src_height = src.get_height()

        width, height = self.get_fitting_size((src_width, src_height),
                                              (width, height),
                                              keep_ratio=keep_ratio,
                                              scale_up=scale_up)

        if (width, height) != (src_width, src_height) and pil_filter > -1:
            # scale by PIL interpolation filter
            src = self.pil_to_pixbuf(self.pixbuf_to_pil(src).resize([width, height],
                                                                    resample=pil_filter))
            src_width = src.get_width()
            src_height = src.get_height()

        if src.get_has_alpha():
            if config['CHECKERED_BG_FOR_TRANSPARENT_IMAGES']:
                check_size, color1, color2 = config['CHECKERED_BG_SIZE'], 0x777777, 0x999999
            else:
                check_size, color1, color2 = 1024, 0xFFFFFF, 0xFFFFFF
            if (width, height) == (src_width, src_height):
                # Using anything other than nearest interpolation will result in a
                # modified image if no resizing takes place (even if it's opaque).
                scaling_quality = GdkPixbuf.InterpType.NEAREST

            src = src.composite_color_simple(width, height, scaling_quality,
                                             255, check_size, color1, color2)
        elif (width, height) != (src_width, src_height):
            src = src.scale_simple(width, height, scaling_quality)

        return self.rotate_pixbuf(src, rotation)

    @staticmethod
    def add_border(pixbuf, thickness: int, color: int = 0x000000FF):
        """
        Return a pixbuf from <pixbuf> with a <thickness> px border of
        <color> added.
        """

        canvas = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8,
                                      pixbuf.get_width() + thickness * 2,
                                      pixbuf.get_height() + thickness * 2)
        canvas.fill(color)
        pixbuf.copy_area(0, 0, pixbuf.get_width(), pixbuf.get_height(),
                         canvas, thickness, thickness)
        return canvas

    @staticmethod
    def pil_to_pixbuf(im, keep_orientation: bool = False):
        """
        Return a pixbuf created from the PIL <im>
        """

        if im.mode.startswith('RGB'):
            has_alpha = im.mode == 'RGBA'
        elif im.mode in ('LA', 'P'):
            has_alpha = True
        else:
            has_alpha = False

        if has_alpha:
            target_mode = 'RGBA'
        else:
            target_mode = 'RGB'

        if im.mode != target_mode:
            im = im.convert(target_mode)
        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(
            GLib.Bytes.new(im.tobytes()), GdkPixbuf.Colorspace.RGB,
            has_alpha, 8,
            im.size[0], im.size[1],
            (4 if has_alpha else 3) * im.size[0]
        )
        if keep_orientation:
            # Keep orientation metadata.
            orientation = im.getexif().get(274, None)
            if orientation is not None:
                setattr(pixbuf, 'orientation', str(orientation))
        return pixbuf

    @staticmethod
    def pixbuf_to_pil(pixbuf):
        """
        Return a PIL image created from <pixbuf>
        """

        dimensions = pixbuf.get_width(), pixbuf.get_height()
        stride = pixbuf.get_rowstride()
        pixels = pixbuf.get_pixels()
        mode = 'RGBA' if pixbuf.get_has_alpha() else 'RGB'
        return Image.frombuffer(mode, dimensions, pixels, 'raw', mode, stride, 1)

    @staticmethod
    def is_animation(pixbuf):
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

    def load_animation(self, im):
        if im.format == 'GIF' and im.mode == 'P':
            # TODO: Pillow has bug with gif animation
            # https://github.com/python-pillow/Pillow/labels/GIF
            #
            # Pillow has bug with gif animation, fallback to GdkPixbuf
            raise NotImplementedError
        anime = AnimeFrameBuffer(im.n_frames, loop=im.info['loop'])
        background = im.info.get('background', None)
        if isinstance(background, tuple):
            color = 0
            for n, c in enumerate(background):
                color |= c << n * 8
            background = color
        frameiter = ImageSequence.Iterator(im)
        for n, frame in enumerate(frameiter):
            anime.add_frame(n, self.pil_to_pixbuf(frame),
                            int(frame.info.get('duration', 0)),
                            background=background)
        return anime.create_animation()

    def load_pixbuf(self, path: Path):
        """
        Loads a pixbuf from a given image file
        """

        enable_anime = config['ANIMATION_MODE'] != Constants.ANIMATION['DISABLED']
        try:
            with LockedFileIO(path) as fio:
                with Image.open(fio) as im:
                    # make sure n_frames loaded
                    im.load()
                    if enable_anime and im.is_animated:
                        return self.load_animation(im)
                    return self.pil_to_pixbuf(im, keep_orientation=True)
        except Exception as ex:
            # should only be hit when loading trying to load a gif
            logger.debug(f'failed to load pixbuf: {ex}')

        if enable_anime:
            pixbuf = GdkPixbuf.PixbufAnimation.new_from_file(str(path))
            if pixbuf.is_static_image():
                return pixbuf.get_static_image()
            return pixbuf

        return GdkPixbuf.Pixbuf.new_from_file(str(path))

    def load_pixbuf_size(self, path: Path, width: int, height: int):
        """
        Loads a pixbuf from a given image file and scale it to fit inside (width, height)
        """

        try:
            with LockedFileIO(path) as fio:
                with Image.open(fio) as im:
                    im.thumbnail((width, height), resample=Image.BOX)
                    return self.pil_to_pixbuf(im, keep_orientation=True)
        except Exception as ex:
            logger.error(f'failed to load pixbuf: {ex}')

    def load_pixbuf_data(self, imgdata):
        """
        Loads a pixbuf from the data passed in <imgdata>
        """

        try:
            with Image.open(BytesIO(imgdata)) as im:
                return self.pil_to_pixbuf(im, keep_orientation=True)
        except Exception as ex:
            logger.error(f'failed to load pixbuf: {ex}')

    def enhance(self, pixbuf, brightness: float = 1.0, contrast: float = 1.0,
                saturation: float = 1.0, sharpness: float = 1.0, autocontrast: bool = False):
        """
        Return a modified pixbuf from <pixbuf> where the enhancement operations
        corresponding to each argument has been performed. A value of 1.0 means
        no change. If <autocontrast> is True it overrides the <contrast> value,
        but only if the image mode is supported by ImageOps.autocontrast (i.e.
        it is L or RGB.)
        """

        if self.is_animation(pixbuf):
            return AnimeFrameExecutor.frame_executor(
                pixbuf, self.enhance,
                kwargs=dict(
                    brightness=brightness, contrast=contrast,
                    saturation=saturation, sharpness=1.0,
                    autocontrast=False
                )
            )
        im = self.pixbuf_to_pil(pixbuf)
        if brightness != 1.0:
            im = ImageEnhance.Brightness(im).enhance(brightness)
        if autocontrast and im.mode in ('L', 'RGB'):
            im = ImageOps.autocontrast(im, cutoff=0.1)
        elif contrast != 1.0:
            im = ImageEnhance.Contrast(im).enhance(contrast)
        if saturation != 1.0:
            im = ImageEnhance.Color(im).enhance(saturation)
        if sharpness != 1.0:
            im = ImageEnhance.Sharpness(im).enhance(sharpness)
        return self.pil_to_pixbuf(im)

    @staticmethod
    def get_implied_rotation(pixbuf):
        """
        Return the implied rotation in degrees: 0, 90, 180, or 270.
        The implied rotation is the angle (in degrees) that the raw pixbuf should
        be rotated in order to be displayed "correctly". E.g. a photograph taken
        by a camera that is held sideways might store this fact in its Exif data,
        and the pixbuf loader will set the orientation option correspondingly
        """

        try:
            orientation = pixbuf.orientation
            if orientation == '3':
                return 180
            elif orientation == '6':
                return 90
            elif orientation == '8':
                return 270
        except AttributeError:
            pass

        return 0

    @staticmethod
    def get_image_size(path: Path):
        """
        Return image informations: (format, width, height)
        """

        with LockedFileIO(path) as fio:
            with Image.open(fio) as im:
                return im.size

    @staticmethod
    def get_image_mime(path: Path):
        """
        Return image informations: (format, width, height)
        """

        with LockedFileIO(path) as fio:
            with Image.open(fio) as im:
                return im.format


ImageTools = _ImageTools()
