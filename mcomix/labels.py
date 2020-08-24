# -*- coding: utf-8 -*-

from gi.repository import GLib, Gtk, Pango


class FormattedLabel(Gtk.Label):
    """
    FormattedLabel keeps a label always formatted with some pango weight,
    style and scale, even when new text is set using set_text()
    """

    _STYLES = {
        Pango.Style.NORMAL: 'normal',
        Pango.Style.OBLIQUE: 'oblique',
        Pango.Style.ITALIC: 'italic',
    }

    def __init__(self, text='', weight=Pango.Weight.NORMAL, style=Pango.Style.NORMAL, scale=1.0):
        super(FormattedLabel, self).__init__()
        self.__weight = weight
        self.__style = style
        self.__scale = scale
        self.set_text(text)

    def set_text(self, text):
        markup = '<span font_size="%u" font_weight="%u"font_style="%s">%s</span>' % (
            int(self.__scale * 10 * 1024),
            self.__weight,
            self._STYLES[self.__style],
            GLib.markup_escape_text(text))
        self.set_markup(markup)


class BoldLabel(FormattedLabel):
    """
    A FormattedLabel that is always bold and otherwise normal
    """

    def __init__(self, text=''):
        super(BoldLabel, self).__init__(text=text, weight=Pango.Weight.BOLD)


class ItalicLabel(FormattedLabel):
    """
    A FormattedLabel that is always italic and otherwise normal
    """

    def __init__(self, text=''):
        super(ItalicLabel, self).__init__(text=text, style=Pango.Style.ITALIC)
