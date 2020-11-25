# -*- coding: utf-8 -*-

"""enhance_backend.py - Image enhancement handler and dialog (e.g. contrast, brightness etc.)"""

from mcomix.image_tools import ImageTools
from mcomix.preferences import config


class ImageEnhancer:
    """
    The ImageEnhancer keeps track of the "enhancement" values and performs
    these enhancements on pixbufs. Changes to the ImageEnhancer's values
    can be made using an _EnhanceImageDialog
    """

    def __init__(self, window):
        super().__init__()

        self.__window = window

        self.__brightness = config['BRIGHTNESS']
        self.__contrast = config['CONTRAST']
        self.__saturation = config['SATURATION']
        self.__sharpness = config['SHARPNESS']
        self.__autocontrast = config['AUTO_CONTRAST']

    @property
    def brightness(self):
        return self.__brightness

    @brightness.setter
    def brightness(self, value: float):
        self.__brightness = value

    @property
    def contrast(self):
        return self.__contrast

    @contrast.setter
    def contrast(self, value: float):
        self.__contrast = value

    @property
    def saturation(self):
        return self.__saturation

    @saturation.setter
    def saturation(self, value: float):
        self.__saturation = value

    @property
    def sharpness(self):
        return self.__sharpness

    @sharpness.setter
    def sharpness(self, value: float):
        self.__sharpness = value

    @property
    def autocontrast(self):
        return self.__autocontrast

    @autocontrast.setter
    def autocontrast(self, value: bool):
        self.__autocontrast = value

    def enhance(self, pixbuf):
        """
        Return an "enhanced" version of <pixbuf>
        """

        if (self.brightness or self.contrast or self.saturation or self.sharpness or self.autocontrast) != 1.0:
            return ImageTools.enhance(pixbuf, self.brightness, self.contrast,
                                      self.saturation, self.sharpness, self.autocontrast)
        return pixbuf

    def signal_update(self):
        """
        Signal to the main window that a change in the enhancement values has been made
        """

        self.__window.draw_image()
