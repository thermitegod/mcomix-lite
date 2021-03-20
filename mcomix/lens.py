# -*- coding: utf-8 -*-

"""lens.py - Magnifying lens"""

import math

from gi.repository import Gdk, GdkPixbuf, Gtk

from mcomix.constants import Constants
from mcomix.image_tools import ImageTools
from mcomix.preferences import config


class MagnifyingLens:
    """
    The MagnifyingLens creates cursors from the raw pixbufs containing
    the unscaled data for the currently displayed images. It does this by
    looking at the cursor position and calculating what image data to put
    in the "lens" cursor.
    Note: The mapping is highly dependent on the exact layout of the main
    window images, thus this module isn't really independent from the main
    module as it uses implementation details not in the interface
    """

    def __init__(self, window):
        super().__init__()

        self.__window = window
        self.__area = self.__window.get_main_layout()
        self.__area.connect('motion-notify-event', self._motion_event)

        #: Stores lens state
        self.__enabled = False
        #: Stores a tuple of the last mouse coordinates
        self.__point = None
        #: Stores the last rectangle that was used to render the lens
        self.__last_lens_rect = None

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, enabled):
        if self.__window.imagehandler.get_number_of_pages() == 0:
            return

        self.__enabled = enabled

        if self.__enabled:
            self.__window.cursor_handler.set_cursor_type(Constants.CURSOR['NONE'])

            if self.__point:
                self._draw_lens(*self.__point)
        else:
            self.__window.cursor_handler.set_cursor_type(Constants.CURSOR['NORMAL'])
            self._clear_lens()
            self.__last_lens_rect = None

    def _draw_lens(self, x: int, y: int):
        """
        Calculate what image data to put in the lens and update the cursor
        with it; <x> and <y> are the positions of the cursor within the
        main window layout area
        """

        if self.__window.images[0].get_storage_type() not in (Gtk.ImageType.PIXBUF, Gtk.ImageType.ANIMATION):
            return

        rectangle = self._calculate_lens_rect(x, y, config['LENS_SIZE'], config['LENS_SIZE'])
        pixbuf = self._get_lens_pixbuf(x, y)

        draw_region = Gdk.Rectangle()
        draw_region.x, draw_region.y, draw_region.width, draw_region.height = rectangle
        if self.__last_lens_rect:
            last_region = Gdk.Rectangle()
            last_region.x, last_region.y, last_region.width, last_region.height = self.__last_lens_rect
            draw_region = Gdk.rectangle_union(draw_region, last_region)

        window = self.__window.get_main_layout().get_bin_window()
        window.begin_paint_rect(draw_region)

        self._clear_lens()

        cr = window.cairo_create()
        surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf, 0, window)
        cr.set_source_surface(surface, rectangle[0], rectangle[1])
        cr.paint()

        window.end_paint()

        self.__last_lens_rect = rectangle

    def _calculate_lens_rect(self, x: int, y: int, width: int, height: int):
        """
        Calculates the area where the lens will be drawn on screen. This method takes
        screen space into calculation and moves the rectangle accordingly when the the rectangle
        would otherwise flow over the allocated area
        """

        lens_x = max(x - width // 2, 0)
        lens_y = max(y - height // 2, 0)

        max_width, max_height = self.__window.get_visible_area_size()
        max_width += int(self.__window.get_hadjust().get_value())
        max_height += int(self.__window.get_vadjust().get_value())
        lens_x = min(lens_x, max_width - width)
        lens_y = min(lens_y, max_height - height)

        # Don't forget 1 pixel border...
        return lens_x, lens_y, width + 2, height + 2

    def _clear_lens(self):
        """
        Invalidates the area that was damaged by the last call to draw_lens
        """

        if not self.__last_lens_rect:
            return

        window = self.__window.get_main_layout().get_bin_window()
        crect = Gdk.Rectangle()
        crect.x, crect.y, crect.width, crect.height = self.__last_lens_rect
        window.invalidate_rect(crect, True)
        window.process_updates(True)
        self.__last_lens_rect = None

    def toggle(self, value: bool):
        """
        Toggle on or off the lens depending on the state of <action>
        """

        self.enabled = value

    def _motion_event(self, widget, event):
        """
        Called whenever the mouse moves over the image area
        """

        self.__point = (int(event.x), int(event.y))
        if self.enabled:
            self._draw_lens(*self.__point)

    def _get_lens_pixbuf(self, x: int, y: int):
        """
        Get a pixbuf containing the appropiate image data for the lens
        where <x> and <y> are the positions of the cursor
        """

        canvas = GdkPixbuf.Pixbuf.new(colorspace=GdkPixbuf.Colorspace.RGB,
                                      has_alpha=True, bits_per_sample=8,
                                      width=config['LENS_SIZE'],
                                      height=config['LENS_SIZE'])
        canvas.fill(0x000000FF)  # black
        cb = self.__window.get_layout().get_content_boxes()
        source_pixbufs = self.__window.imagehandler.get_pixbufs(len(cb))
        for idx, item in enumerate(cb):
            if ImageTools.is_animation(source_pixbufs[idx]):
                continue
            cpos = cb[idx].get_position()
            self._add_subpixbuf(canvas, x - cpos[0], y - cpos[1], cb[idx].get_size(), source_pixbufs[idx])

        return ImageTools.add_border(canvas, 1)

    def _add_subpixbuf(self, canvas, x: int, y: int, image_size: tuple, source_pixbuf):
        """
        Copy a subpixbuf from <source_pixbuf> to <canvas> as it should
        be in the lens if the coordinates <x>, <y> are the mouse pointer
        position on the main window layout area.
        The displayed image (scaled from the <source_pixbuf>) must have
        size <image_size>
        """

        # Prevent division by zero exceptions further down
        if not image_size[0]:
            return

        # FIXME This merely prevents Errors being raised if source_pixbuf is an
        # animation. The result might be broken, though, since animation,
        # rotation etc. might not match or will be ignored:
        source_pixbuf = ImageTools.static_image(source_pixbuf)

        rotation = config['ROTATION']
        if config['AUTO_ROTATE_FROM_EXIF']:
            rotation += ImageTools.get_implied_rotation(source_pixbuf)
            rotation %= 360

        if rotation in [90, 270]:
            scale = source_pixbuf.get_height() / image_size[0]
        else:
            scale = source_pixbuf.get_width() / image_size[0]

        x *= scale
        y *= scale

        source_mag = config['LENS_MAGNIFICATION'] / scale
        width = height = config['LENS_SIZE'] / source_mag

        paste_left = x > width / 2
        paste_top = y > height / 2
        dest_x = max(0, int(math.ceil((width / 2 - x) * source_mag)))
        dest_y = max(0, int(math.ceil((height / 2 - y) * source_mag)))

        if rotation == 90:
            x, y = y, source_pixbuf.get_height() - x
        elif rotation == 180:
            x = source_pixbuf.get_width() - x
            y = source_pixbuf.get_height() - y
        elif rotation == 270:
            x, y = source_pixbuf.get_width() - y, x

        if config['HORIZONTAL_FLIP']:
            if rotation in (90, 270):
                y = source_pixbuf.get_height() - y
            else:
                x = source_pixbuf.get_width() - x
        if config['VERTICAL_FLIP']:
            if rotation in (90, 270):
                x = source_pixbuf.get_width() - x
            else:
                y = source_pixbuf.get_height() - y

        src_x = x - width / 2
        src_y = y - height / 2
        if src_x < 0:
            width += src_x
            src_x = 0
        if src_y < 0:
            height += src_y
            src_y = 0
        width = max(0, min(source_pixbuf.get_width() - src_x, width))
        height = max(0, min(source_pixbuf.get_height() - src_y, height))
        if width < 1 or height < 1:
            return

        subpixbuf = source_pixbuf.new_subpixbuf(int(src_x), int(src_y), int(width), int(height))
        subpixbuf = subpixbuf.scale_simple(
            int(math.ceil(source_mag * subpixbuf.get_width())),
            int(math.ceil(source_mag * subpixbuf.get_height())),
            config['SCALING_QUALITY'])

        if rotation == 90:
            subpixbuf = subpixbuf.rotate_simple(GdkPixbuf.PixbufRotation.CLOCKWISE)
        elif rotation == 180:
            subpixbuf = subpixbuf.rotate_simple(GdkPixbuf.PixbufRotation.UPSIDEDOWN)
        elif rotation == 270:
            subpixbuf = subpixbuf.rotate_simple(GdkPixbuf.PixbufRotation.COUNTERCLOCKWISE)

        if config['HORIZONTAL_FLIP']:
            subpixbuf = subpixbuf.flip(horizontal=True)
        if config['VERTICAL_FLIP']:
            subpixbuf = subpixbuf.flip(horizontal=False)

        subpixbuf = self.__window.enhancer.enhance(subpixbuf)

        if paste_left:
            dest_x = 0
        else:
            dest_x = min(canvas.get_width() - subpixbuf.get_width(), dest_x)
        if paste_top:
            dest_y = 0
        else:
            dest_y = min(canvas.get_height() - subpixbuf.get_height(), dest_y)

        if subpixbuf.get_has_alpha() and config['CHECKERED_BG_FOR_TRANSPARENT_IMAGES']:
            subpixbuf = subpixbuf.composite_color_simple(subpixbuf.get_width(), subpixbuf.get_height(),
                                                         GdkPixbuf.InterpType.NEAREST, 255, 8, 0x777777, 0x999999)

        subpixbuf.copy_area(0, 0, subpixbuf.get_width(), subpixbuf.get_height(), canvas, dest_x, dest_y)
