from __future__ import annotations

import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageOps as ImageOps
from gi.repository import Gtk

from mcomix.image_handler import ImageHandler
from mcomix.image_tools import ImageTools
from mcomix.lib.events import Events, EventType
from mcomix.preferences import config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class EnhanceImageDialog(Gtk.Dialog):
    def __init__(self, window: MainWindow):
        super().__init__()

        self.set_transient_for(window)

        self.__events = Events()
        self.__events.add_event(EventType.FILE_CLOSED, self._on_book_close)
        self.__events.add_event(EventType.PAGE_AVAILABLE, self._on_page_available)
        self.__events.add_event(EventType.PAGE_CHANGED, self._on_page_change)

        self.__image_handler = ImageHandler()

        reset = Gtk.Button.new_with_label('Reset')
        self.add_action_widget(reset, Gtk.ResponseType.REJECT)
        save = Gtk.Button.new_with_label('Save')
        self.add_action_widget(save, Gtk.ResponseType.APPLY)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.set_resizable(False)
        self.connect('response', self._response)
        self.set_default_response(Gtk.ResponseType.OK)

        self.__pixbuf = None

        vbox = Gtk.VBox(homogeneous=False, spacing=10)
        self.set_border_width(4)
        vbox.set_border_width(6)
        self.vbox.add(vbox)

        self.__hist_image = Gtk.Image()
        self.__hist_image.set_size_request(262, 170)
        vbox.pack_start(self.__hist_image, True, True, 0)
        vbox.pack_start(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), True, True, 0)

        hbox = Gtk.HBox(homogeneous=False, spacing=4)
        vbox.pack_start(hbox, False, False, 2)
        vbox_left = Gtk.VBox(homogeneous=False, spacing=4)
        vbox_right = Gtk.VBox(homogeneous=False, spacing=4)
        hbox.pack_start(vbox_left, False, False, 2)
        hbox.pack_start(vbox_right, True, True, 2)

        def _create_scale(label_text: str, config_key: str):
            label = Gtk.Label(label=label_text)
            label.set_xalign(1.0)
            label.set_yalign(0.5)
            label.set_use_underline(True)
            vbox_left.pack_start(label, True, False, 2)
            adj = Gtk.Adjustment(value=0.0, lower=-1.0, upper=1.0, step_increment=0.01, page_increment=0.1)
            scale = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, adj)
            scale.set_digits(2)
            scale.set_value(config[config_key] - 1)
            scale.set_value_pos(Gtk.PositionType.RIGHT)
            scale.connect('value-changed', self._change_values)
            label.set_mnemonic_widget(scale)
            vbox_right.pack_start(scale, True, False, 2)
            return scale

        self.__brightness_scale = _create_scale('Brightness:', 'BRIGHTNESS')
        self.__contrast_scale = _create_scale('Contrast:', 'CONTRAST')
        self.__saturation_scale = _create_scale('Saturation:', 'SATURATION')
        self.__sharpness_scale = _create_scale('Sharpness:', 'SHARPNESS')

        vbox.pack_start(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), True, True, 0)

        self.__autocontrast_button = Gtk.CheckButton.new_with_mnemonic('_Automatically adjust contrast')
        vbox.pack_start(self.__autocontrast_button, False, False, 2)
        self.__autocontrast_button.connect('toggled', self._change_values)
        self.__autocontrast_button.set_active(config['AUTO_CONTRAST'])
        self.__contrast_scale.set_sensitive(not self.__autocontrast_button.get_active())

        self._on_page_change()

        self.show_all()

    def draw_histogram(self, height: int = 170, fill: int = 170):
        """
        Draw a histogram (RGB) from self.__pixbuf and return it as another pixbuf.

        :param height: height of the returned pixbuf
        :param fill: determines the color intensity of the filled graphs,
               valid values are between 0 and 255.
        :returns: modified pixbuf, the returned prixbuf will be 262x<height> px.
        """

        self.__pixbuf = ImageTools.static_image(self.__pixbuf)

        im = Image.new('RGB', (258, height - 4), (30, 30, 30))
        hist_data = ImageTools.pixbuf_to_pil(self.__pixbuf).histogram()
        maximum = max(hist_data[:768] + [1])
        y_scale = (height - 6) / maximum
        r = [int(hist_data[n] * y_scale) for n in range(256)]
        g = [int(hist_data[n] * y_scale) for n in range(256, 512)]
        b = [int(hist_data[n] * y_scale) for n in range(512, 768)]
        im_data = im.getdata()

        # Draw the filling colors
        for x in range(256):
            for y in range(1, max(r[x], g[x], b[x]) + 1):
                r_px = fill if y <= r[x] else 0
                g_px = fill if y <= g[x] else 0
                b_px = fill if y <= b[x] else 0
                im_data.putpixel((x + 1, height - 5 - y), (r_px, g_px, b_px))

        # Draw the outlines
        for x in range(1, 256):
            # channel r
            for y in list(range(r[x-1] + 1, r[x] + 1)) + [r[x]] * (r[x] != 0):
                r_px, g_px, b_px = im_data.getpixel((x + 1, height - 5 - y))
                im_data.putpixel((x + 1, height - 5 - y), (255, g_px, b_px))
            for y in range(r[x] + 1, r[x-1] + 1):
                r_px, g_px, b_px = im_data.getpixel((x, height - 5 - y))
                im_data.putpixel((x, height - 5 - y), (255, g_px, b_px))

            # channel g
            for y in list(range(g[x-1] + 1, g[x] + 1)) + [g[x]] * (g[x] != 0):
                r_px, g_px, b_px = im_data.getpixel((x + 1, height - 5 - y))
                im_data.putpixel((x + 1, height - 5 - y), (r_px, 255, b_px))
            for y in range(g[x] + 1, g[x-1] + 1):
                r_px, g_px, b_px = im_data.getpixel((x, height - 5 - y))
                im_data.putpixel((x, height - 5 - y), (r_px, 255, b_px))

            # channel b
            for y in list(range(b[x-1] + 1, b[x] + 1)) + [b[x]] * (b[x] != 0):
                r_px, g_px, b_px = im_data.getpixel((x + 1, height - 5 - y))
                im_data.putpixel((x + 1, height - 5 - y), (r_px, g_px, 255))
            for y in list(range(b[x] + 1, b[x-1] + 1)):
                r_px, g_px, b_px = im_data.getpixel((x, height - 5 - y))
                im_data.putpixel((x, height - 5 - y), (r_px, g_px, 255))

        if config['ENHANCE_EXTRA']:
            # if True a label with the maximum pixel value will be added to one corner
            maxstr = f'max pixel value: {maximum}'
            draw = ImageDraw.Draw(im)
            draw.rectangle((0, 0, len(maxstr) * 6 + 2, 10), fill=(30, 30, 30))
            draw.text((2, 0), maxstr, fill=(255, 255, 255))

        im = ImageOps.expand(im, 1, (80, 80, 80))
        im = ImageOps.expand(im, 1, (0, 0, 0))

        self.__hist_image.set_from_pixbuf(ImageTools.pil_to_pixbuf(im))

    def _on_book_close(self):
        self.clear_histogram()

    def _on_page_change(self):
        if not self.__image_handler.page_is_available():
            self.clear_histogram()
            return
        # XXX transitional(double page limitation)
        self.__pixbuf = self.__image_handler.get_pixbufs(1)[0]
        self.draw_histogram()

    def _on_page_available(self, page_number):
        current_page_number = self.__image_handler.get_current_page()
        if current_page_number == page_number:
            self._on_page_change()

    def clear_histogram(self):
        """
        Clear the histogram in the dialog
        """

        self.__pixbuf = None
        self.__hist_image.clear()

    def _change_values(self, *args):
        config['BRIGHTNESS'] = self.__brightness_scale.get_value() + 1
        config['CONTRAST'] = self.__contrast_scale.get_value() + 1
        config['SATURATION'] = self.__saturation_scale.get_value() + 1
        config['SHARPNESS'] = self.__sharpness_scale.get_value() + 1
        config['AUTO_CONTRAST'] = self.__autocontrast_button.get_active()
        self.__contrast_scale.set_sensitive(not self.__autocontrast_button.get_active())
        self.__events.run_events(EventType.DRAW_PAGE)

    def _response(self, dialog, response: int):
        match response:
            case (Gtk.ResponseType.OK | Gtk.ResponseType.DELETE_EVENT):
                self.destroy()

            case Gtk.ResponseType.APPLY:
                self._change_values(self)

            case Gtk.ResponseType.REJECT:
                self.__brightness_scale.set_value(0.0)
                self.__contrast_scale.set_value(0.0)
                self.__saturation_scale.set_value(0.0)
                self.__sharpness_scale.set_value(0.0)
                self.__autocontrast_button.set_active(False)
                self._change_values(self)
