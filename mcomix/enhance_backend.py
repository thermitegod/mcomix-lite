# -*- coding: utf-8 -*-

"""enhance_backend.py - Image enhancement handler and dialog (e.g. contrast, brightness etc.)"""

from mcomix import image_tools
from mcomix.preferences import prefs


class ImageEnhancer:
    """The ImageEnhancer keeps track of the "enhancement" values and performs
    these enhancements on pixbufs. Changes to the ImageEnhancer's values
    can be made using an _EnhanceImageDialog"""

    def __init__(self, window):
        self.__window = window
        self.__brightness = prefs['brightness']
        self.__contrast = prefs['contrast']
        self.__saturation = prefs['saturation']
        self.__sharpness = prefs['sharpness']
        self.__autocontrast = prefs['auto contrast']

    def enhance(self, pixbuf):
        """Return an "enhanced" version of <pixbuf>"""
        if (self.__brightness != 1.0 or self.__contrast != 1.0 or
                self.__saturation != 1.0 or self.__sharpness != 1.0 or
                self.__autocontrast):
            return image_tools.enhance(pixbuf, self.__brightness, self.__contrast,
                                       self.__saturation, self.__sharpness, self.__autocontrast)

        return pixbuf

    def signal_update(self):
        """Signal to the main window that a change in the enhancement values has been made"""
        self.__window.draw_image()

    def get_brightness(self):
        return self.__brightness

    def get_contrast(self):
        return self.__contrast

    def get_saturation(self):
        return self.__saturation

    def get_sharpness(self):
        return self.__sharpness

    def get_autocontrast(self):
        return self.__autocontrast

    def set_brightness(self, value):
        self.__brightness = value

    def set_contrast(self, value):
        self.__contrast = value

    def set_saturation(self, value):
        self.__saturation = value

    def set_sharpness(self, value):
        self.__sharpness = value

    def set_autocontrast(self, value):
        self.__autocontrast = value
