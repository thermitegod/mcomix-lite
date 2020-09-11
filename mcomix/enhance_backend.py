# -*- coding: utf-8 -*-

"""enhance_backend.py - Image enhancement handler and dialog (e.g. contrast, brightness etc.)"""

from mcomix.image_tools import ImageTools
from mcomix.preferences import prefs


class ImageEnhancer:
    """
    The ImageEnhancer keeps track of the "enhancement" values and performs
    these enhancements on pixbufs. Changes to the ImageEnhancer's values
    can be made using an _EnhanceImageDialog
    """

    def __init__(self, window):
        super().__init__()

        self.__window = window
        self.brightness = prefs['BRIGHTNESS']
        self.contrast = prefs['CONTRAST']
        self.saturation = prefs['SATURATION']
        self.sharpness = prefs['SHARPNESS']
        self.autocontrast = prefs['AUTO_CONTRAST']

    def enhance(self, pixbuf):
        """
        Return an "enhanced" version of <pixbuf>
        """

        if (self.brightness != 1.0 or self.contrast != 1.0 or
                self.saturation != 1.0 or self.sharpness != 1.0 or
                self.autocontrast):
            return ImageTools.enhance(pixbuf, self.brightness, self.contrast,
                                      self.saturation, self.sharpness, self.autocontrast)

        return pixbuf

    def signal_update(self):
        """
        Signal to the main window that a change in the enhancement values has been made
        """

        self.__window.draw_image()
