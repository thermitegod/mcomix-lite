# -*- coding: utf-8 -*-

"""image_tools.py - Various image manipulations"""

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps, ImageSequence
from PIL.JpegImagePlugin import _getexif
from gi.repository import GLib, Gdk, GdkPixbuf, Gio

from mcomix import anime_tools, constants
from mcomix.lib import reader
from mcomix.preferences import prefs

GTK_GDK_COLOR_BLACK = Gdk.color_parse('black')
GTK_GDK_COLOR_WHITE = Gdk.color_parse('white')


def rotate_pixbuf(src, rotation):
    rotation %= 360
    if rotation == 0:
        return src
    if rotation == 90:
        return src.rotate_simple(GdkPixbuf.PixbufRotation.CLOCKWISE)
    if rotation == 180:
        return src.rotate_simple(GdkPixbuf.PixbufRotation.UPSIDEDOWN)
    if rotation == 270:
        return src.rotate_simple(GdkPixbuf.PixbufRotation.COUNTERCLOCKWISE)
    raise ValueError(f'unsupported rotation: {rotation}')


def get_fitting_size(source_size, target_size, keep_ratio=True, scale_up=False):
    """Return a scaled version of <source_size>
    small enough to fit in <target_size>.
    Both <source_size> and <target_size>
    must be (width, height) tuples.
    If <keep_ratio> is True, aspect ratio is kept.
    If <scale_up> is True, <source_size> is scaled up
    when smaller than <target_size>"""
    width, height = target_size
    src_width, src_height = source_size
    if not scale_up and src_width <= width and src_height <= height:
        width, height = src_width, src_height
    else:
        if keep_ratio:
            if float(src_width) / width > float(src_height) / height:
                height = int(max(src_height * width / src_width, 1))
            else:
                width = int(max(src_width * height / src_height, 1))
    return width, height


def trans_pixbuf(src, flip=False, flop=False):
    if is_animation(src):
        return anime_tools.frame_executor(
                src, trans_pixbuf,
                kwargs=dict(flip=flip, flop=flop)
        )
    if flip:
        src = src.flip(horizontal=False)
    if flop:
        src = src.flip(horizontal=True)
    return src


def fit_pixbuf_to_rectangle(src, rect, rotation):
    if is_animation(src):
        return anime_tools.frame_executor(
                src, fit_pixbuf_to_rectangle,
                args=(rect, rotation)
        )
    return fit_in_rectangle(src, rect[0], rect[1],
                            rotation=rotation,
                            keep_ratio=False,
                            scale_up=True)


def fit_in_rectangle(src, width, height, keep_ratio=True, scale_up=False,
                     rotation=0, scaling_quality=None):
    """Scale (and return) a pixbuf so that it fits in a rectangle with
    dimensions <width> x <height>. A negative <width> or <height>
    means an unbounded dimension - both cannot be negative.

    If <rotation> is 90, 180 or 270 we rotate <src> first so that the
    rotated pixbuf is fitted in the rectangle.

    Unless <scale_up> is True we don't stretch images smaller than the
    given rectangle.

    If <keep_ratio> is True, the image ratio is kept, and the result
    dimensions may be smaller than the target dimensions.

    If <src> has an alpha channel it gets a checkboard background"""
    # "Unbounded" really means "bounded to 10000 px" - for simplicity.
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
        scaling_quality = prefs['scaling quality']

    src_width = src.get_width()
    src_height = src.get_height()

    width, height = get_fitting_size((src_width, src_height),
                                     (width, height),
                                     keep_ratio=keep_ratio,
                                     scale_up=scale_up)

    if src.get_has_alpha():
        if prefs['checkered bg for transparent images']:
            check_size, color1, color2 = 8, 0x777777, 0x999999
        else:
            check_size, color1, color2 = 1024, 0xFFFFFF, 0xFFFFFF
        if width == src_width and height == src_height:
            # Using anything other than nearest interpolation will result in a
            # modified image if no resizing takes place (even if it's opaque).
            scaling_quality = GdkPixbuf.InterpType.NEAREST
        src = src.composite_color_simple(width, height, scaling_quality,
                                         255, check_size, color1, color2)
    elif width != src_width or height != src_height:
        src = src.scale_simple(width, height, scaling_quality)

    src = rotate_pixbuf(src, rotation)

    return src


def add_border(pixbuf, thickness, color=0x000000FF):
    """Return a pixbuf from <pixbuf> with a <thickness> px border of
    <color> added.
    """
    canvas = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8,
                                  pixbuf.get_width() + thickness * 2,
                                  pixbuf.get_height() + thickness * 2)
    canvas.fill(color)
    pixbuf.copy_area(0, 0, pixbuf.get_width(), pixbuf.get_height(),
                     canvas, thickness, thickness)
    return canvas


def pil_to_pixbuf(im, keep_orientation=False):
    """Return a pixbuf created from the PIL <im>."""
    if im.mode.startswith('RGB'):
        has_alpha = im.mode == 'RGBA'
    elif im.mode in ('LA', 'P'):
        has_alpha = True
    else:
        has_alpha = False
    if im.mode != (target_mode := 'RGBA' if has_alpha else 'RGB'):
        im = im.convert(target_mode)
    pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(
            GLib.Bytes.new(im.tobytes()), GdkPixbuf.Colorspace.RGB,
            has_alpha, 8,
            im.size[0], im.size[1],
            (4 if has_alpha else 3) * im.size[0]
    )
    if keep_orientation:
        # Keep orientation metadata.
        if (orientation := _getexif(im).get(274, None)) is not None:
            setattr(pixbuf, 'orientation', str(orientation))
    return pixbuf


def pixbuf_to_pil(pixbuf):
    """Return a PIL image created from <pixbuf>"""
    dimensions = pixbuf.get_width(), pixbuf.get_height()
    stride = pixbuf.get_rowstride()
    pixels = pixbuf.get_pixels()
    mode = 'RGBA' if pixbuf.get_has_alpha() else 'RGB'
    return Image.frombuffer(mode, dimensions, pixels, 'raw', mode, stride, 1)


def is_animation(pixbuf):
    return isinstance(pixbuf, GdkPixbuf.PixbufAnimation)


def disable_transform(pixbuf):
    if is_animation(pixbuf):
        if not hasattr(pixbuf, 'framebuffer'):
            return True
        if not prefs['animation transform']:
            return True

    return False


def static_image(pixbuf):
    """Returns a non-animated version of the specified pixbuf"""
    if is_animation(pixbuf):
        return pixbuf.get_static_image()

    return pixbuf


def set_from_pixbuf(image, pixbuf):
    if is_animation(pixbuf):
        return image.set_from_animation(pixbuf)

    return image.set_from_pixbuf(pixbuf)


def load_animation(im):
    if im.format == 'GIF' and im.mode == 'P':
        # TODO: Pillow has bug with gif animation
        # https://github.com/python-pillow/Pillow/labels/GIF
        raise NotImplementedError('Pillow has bug with gif animation, fallback to GdkPixbuf')
    anime = anime_tools.AnimeFrameBuffer(im.n_frames, loop=im.info['loop'])
    background = im.info.get('background', None)
    if isinstance(background, tuple):
        color = 0
        for n, c in enumerate(background):
            color |= c << n * 8
        background = color
    frameiter = ImageSequence.Iterator(im)
    for n, frame in enumerate(frameiter):
        anime.add_frame(n, pil_to_pixbuf(frame),
                        int(frame.info.get('duration', 0)),
                        background=background)
    return anime.create_animation()


def load_pixbuf(path):
    """Loads a pixbuf from a given image file"""
    enable_anime = prefs['animation mode'] != constants.ANIMATION_DISABLED
    try:
        with reader.LockedFileIO(path) as fio:
            with Image.open(fio) as im:
                # make sure n_frames loaded
                im.load()
                if enable_anime and getattr(im, 'is_animated', False):
                    return load_animation(im)
                return pil_to_pixbuf(im, keep_orientation=True)
    except Exception:
        pass
    if enable_anime:
        pixbuf = GdkPixbuf.PixbufAnimation.new_from_file(path)
        if pixbuf.is_static_image():
            return pixbuf.get_static_image()
        return pixbuf

    return GdkPixbuf.Pixbuf.new_from_file(path)


def load_pixbuf_size(path, width, height):
    """Loads a pixbuf from a given image file and scale it to fit inside (width, height)"""
    try:
        with reader.LockedFileIO(path) as fio:
            with Image.open(fio) as im:
                im.thumbnail((width, height), resample=Image.BOX)
                return pil_to_pixbuf(im, keep_orientation=True)
    except Exception:
        info, image_width, image_height = GdkPixbuf.Pixbuf.get_file_info(path)
        # If we could not get the image info, still try to load
        # the image to let GdkPixbuf raise the appropriate exception.
        if not info:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        # Don't upscale if smaller than target dimensions!
        if image_width <= width and image_height <= height:
            width, height = image_width, image_height
        # Work around GdkPixbuf bug
        # https://gitlab.gnome.org/GNOME/gdk-pixbuf/issues/45
        # TODO: GIF should be always supported by Pillow.
        #       Is this workaround really needed?
        if info.get_name() == 'gif':
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        else:
            # directly return pixbuf
            return GdkPixbuf.Pixbuf.new_from_file_at_size(path, width, height)
        return fit_in_rectangle(pixbuf, width, height,
                                scaling_quality=GdkPixbuf.InterpType.BILINEAR)


def load_pixbuf_data(imgdata):
    """Loads a pixbuf from the data passed in <imgdata>"""
    try:
        with Image.open(BytesIO(imgdata)) as im:
            return pil_to_pixbuf(im, keep_orientation=True)
    except Exception:
        pass
    loader = GdkPixbuf.PixbufLoader()
    loader.write(imgdata)
    loader.close()
    return loader.get_pixbuf()


def enhance(pixbuf, brightness=1.0, contrast=1.0, saturation=1.0, sharpness=1.0, autocontrast=False):
    """Return a modified pixbuf from <pixbuf> where the enhancement operations
    corresponding to each argument has been performed. A value of 1.0 means
    no change. If <autocontrast> is True it overrides the <contrast> value,
    but only if the image mode is supported by ImageOps.autocontrast (i.e.
    it is L or RGB.)"""
    if is_animation(pixbuf):
        return anime_tools.frame_executor(
                pixbuf, enhance,
                kwargs=dict(
                        brightness=brightness, contrast=contrast,
                        saturation=saturation, sharpness=1.0,
                        autocontrast=False
                )
        )
    im = pixbuf_to_pil(pixbuf)
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
    return pil_to_pixbuf(im)


def get_implied_rotation(pixbuf):
    """Return the implied rotation in degrees: 0, 90, 180, or 270.
    The implied rotation is the angle (in degrees) that the raw pixbuf should
    be rotated in order to be displayed "correctly". E.g. a photograph taken
    by a camera that is held sideways might store this fact in its Exif data,
    and the pixbuf loader will set the orientation option correspondingly"""
    pixbuf = static_image(pixbuf)
    if (orientation := getattr(pixbuf, 'orientation', None)) is None:
        orientation = pixbuf.get_option('orientation')

    if orientation == '3':
        return 180
    elif orientation == '6':
        return 90
    elif orientation == '8':
        return 270

    return 0


def convert_rgb16list_to_rgba8int(c):
    return 0x000000FF | (c[0] >> 8 << 24) | (c[1] >> 8 << 16) | (c[2] >> 8 << 8)


def rgb_to_y_601(color):
    return color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114


def text_color_for_background_color(bgcolor):
    if rgb_to_y_601(bgcolor) >= 65535.0 / 2.0:
        return GTK_GDK_COLOR_BLACK
    return GTK_GDK_COLOR_WHITE


def get_image_size(path):
    """Return image informations: (format, width, height)"""
    try:
        with reader.LockedFileIO(path) as fio:
            with Image.open(fio) as im:
                return im.size
    except Exception:
        if (info := GdkPixbuf.Pixbuf.get_file_info(path))[0] is None:
            return 0, 0

        return info[1], info[2]


def get_image_mime(path):
    """Return image informations: (format, width, height)"""
    try:
        with reader.LockedFileIO(path) as fio:
            with Image.open(fio) as im:
                return im.format
    except Exception:
        if (info := GdkPixbuf.Pixbuf.get_file_info(path))[0] is None:
            return 'Unknown filetype'

        return info[0].get_name().upper()


SUPPORTED_IMAGE_EXTS = set()
SUPPORTED_IMAGE_MIMES = set()
SUPPORTED_IMAGE_FORMATS = {}


def init_supported_formats():
    # formats supported by PIL
    # Make sure all supported formats are registered.
    Image.init()
    for ext, name in Image.EXTENSION.items():
        fmt = SUPPORTED_IMAGE_FORMATS.setdefault(name, (set(), set()))
        fmt[1].add(ext.lower())
        mime = Image.MIME.get(
                name, Gio.content_type_guess(filename=f'file{ext}')[0]).lower()
        if mime and mime != 'application/octet-stream':
            fmt[0].add(mime)

    # formats supported by gdk-pixbuf
    for gdkfmt in GdkPixbuf.Pixbuf.get_formats():
        fmt = SUPPORTED_IMAGE_FORMATS.setdefault(
                gdkfmt.get_name().upper(), (set(), set()))
        for m in map(lambda s: s.lower(), gdkfmt.get_mime_types()):
            fmt[0].add(m)
        # get_extensions() return extensions without '.'
        for e in map(lambda s: f'.{s.lower()}', gdkfmt.get_extensions()):
            fmt[1].add(e)
            m = Gio.content_type_guess(filename=f'file{e}')[0].lower()
            if m and m != 'application/octet-stream':
                fmt[0].add(m)

    # cache a supported extensions list
    for mimes, exts in SUPPORTED_IMAGE_FORMATS.values():
        SUPPORTED_IMAGE_EXTS.update(exts)
        SUPPORTED_IMAGE_MIMES.update(mimes)


def is_image_file(path, check_mimetype=False):
    # if check_mimetype is True,
    # read starting bytes and using Gio.content_type_guess
    # to guess if path is supported, ignoring file extension.
    if not SUPPORTED_IMAGE_FORMATS:
        init_supported_formats()
    path = Path(path)
    if prefs['check image mimetype'] and check_mimetype and Path.is_file(path):
        with Path.open(path, mode='rb') as fd:
            magic = fd.read(10)
        mime, uncertain = Gio.content_type_guess(data=magic)
        return mime.lower() in SUPPORTED_IMAGE_MIMES
    return str(path).lower().endswith(tuple(SUPPORTED_IMAGE_EXTS))
