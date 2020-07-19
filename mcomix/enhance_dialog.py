# -*- coding: utf-8 -*-

"""enhance_dialog.py - Image enhancement dialog"""

from gi.repository import Gtk

from mcomix import histogram, image_tools
from mcomix.preferences import prefs


class _EnhanceImageDialog(Gtk.Dialog):
    """A Gtk.Dialog which allows modification of the values belonging to an ImageEnhancer"""

    def __init__(self, window):
        super(_EnhanceImageDialog, self).__init__(title='Enhance image')
        self.set_transient_for(window)

        self.__window = window

        reset = Gtk.Button.new_from_stock(Gtk.STOCK_REVERT_TO_SAVED)
        self.add_action_widget(reset, Gtk.ResponseType.REJECT)
        save = Gtk.Button.new_from_stock(Gtk.STOCK_SAVE)
        self.add_action_widget(save, Gtk.ResponseType.APPLY)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.set_resizable(False)
        self.connect('response', self._response)
        self.set_default_response(Gtk.ResponseType.OK)

        self.__enhancer = window.enhancer
        self.__block = False

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

        def _create_scale(label_text):
            label = Gtk.Label(label=label_text)
            label.set_alignment(1, 0.5)
            label.set_use_underline(True)
            vbox_left.pack_start(label, True, False, 2)
            adj = Gtk.Adjustment(value=0.0, lower=-1.0, upper=1.0, step_increment=0.01, page_increment=0.1)
            scale = Gtk.HScale.new(adj)
            scale.set_digits(2)
            scale.set_value_pos(Gtk.PositionType.RIGHT)
            scale.connect('value-changed', self._change_values)
            # FIXME
            # scale.set_update_policy(Gtk.UPDATE_DELAYED)
            label.set_mnemonic_widget(scale)
            vbox_right.pack_start(scale, True, False, 2)
            return scale

        self.__brightness_scale = _create_scale('_Brightness:')
        self.__contrast_scale = _create_scale('_Contrast:')
        self.__saturation_scale = _create_scale('S_aturation:')
        self.__sharpness_scale = _create_scale('S_harpness:')

        vbox.pack_start(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), True, True, 0)

        self.__autocontrast_button = Gtk.CheckButton.new_with_mnemonic('_Automatically adjust contrast')
        vbox.pack_start(self.__autocontrast_button, False, False, 2)
        self.__autocontrast_button.connect('toggled', self._change_values)

        self.__block = True
        self.__brightness_scale.set_value(self.__enhancer.brightness - 1)
        self.__contrast_scale.set_value(self.__enhancer.contrast - 1)
        self.__saturation_scale.set_value(self.__enhancer.saturation - 1)
        self.__sharpness_scale.set_value(self.__enhancer.sharpness - 1)
        self.__autocontrast_button.set_active(self.__enhancer.autocontrast)
        self.__block = False
        self.__contrast_scale.set_sensitive(not self.__autocontrast_button.get_active())

        self.__window.imagehandler.page_available += self._on_page_available
        self.__window.filehandler.file_closed += self._on_book_close
        self.__window.page_changed += self._on_page_change
        self._on_page_change()

        self.show_all()

    def _on_book_close(self):
        self.clear_histogram()

    def _on_page_change(self):
        if not self.__window.imagehandler.page_is_available():
            self.clear_histogram()
            return
        # XXX transitional(double page limitation)
        pixbuf = self.__window.imagehandler.get_pixbufs(1)[0]
        self.draw_histogram(pixbuf)

    def _on_page_available(self, page_number):
        current_page_number = self.__window.imagehandler.get_current_page()
        if current_page_number == page_number:
            self._on_page_change()

    def draw_histogram(self, pixbuf):
        """Draw a histogram representing <pixbuf> in the dialog"""
        pixbuf = image_tools.static_image(pixbuf)
        histogram_pixbuf = histogram.draw_histogram(pixbuf, text=False)
        self.__hist_image.set_from_pixbuf(histogram_pixbuf)

    def clear_histogram(self):
        """Clear the histogram in the dialog"""
        self.__hist_image.clear()

    def _change_values(self, *args):
        if self.__block:
            return

        self.__enhancer.brightness = self.__brightness_scale.get_value() + 1
        self.__enhancer.contrast = self.__contrast_scale.get_value() + 1
        self.__enhancer.saturation = self.__saturation_scale.get_value() + 1
        self.__enhancer.sharpness = self.__sharpness_scale.get_value() + 1
        self.__enhancer.autocontrast = self.__autocontrast_button.get_active()
        self.__contrast_scale.set_sensitive(not self.__autocontrast_button.get_active())
        self.__enhancer.signal_update()

    def _response(self, dialog, response):
        if response in [Gtk.ResponseType.OK, Gtk.ResponseType.DELETE_EVENT]:
            EnhanceDialog.close_dialog()

        elif response == Gtk.ResponseType.APPLY:
            self._change_values(self)
            prefs['brightness'] = self.__enhancer.brightness()
            prefs['contrast'] = self.__enhancer.contrast()
            prefs['saturation'] = self.__enhancer.saturation()
            prefs['sharpness'] = self.__enhancer.sharpness()
            prefs['auto contrast'] = self.__enhancer.autocontrast()

        elif response == Gtk.ResponseType.REJECT:
            self.__block = True
            self.__brightness_scale.set_value(prefs['brightness'] - 1.0)
            self.__contrast_scale.set_value(prefs['contrast'] - 1.0)
            self.__saturation_scale.set_value(prefs['saturation'] - 1.0)
            self.__sharpness_scale.set_value(prefs['sharpness'] - 1.0)
            self.__autocontrast_button.set_active(prefs['auto contrast'])
            self.__block = False
            self._change_values(self)


class _EnhanceDialog:
    def __init__(self):
        self.__dialog = None

    def open_dialog(self, event, window):
        """Create and display the (singleton) image enhancement dialog"""
        if self.__dialog is None:
            self.__dialog = _EnhanceImageDialog(window)
        else:
            self.__dialog.present()

    def close_dialog(self):
        """Destroy the image enhancement dialog"""
        if self.__dialog is not None:
            self.__dialog.destroy()
            self.__dialog = None


# Singleton instance
EnhanceDialog = _EnhanceDialog()

