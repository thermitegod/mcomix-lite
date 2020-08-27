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

    def __init__(self, text: str = '', weight=Pango.Weight.NORMAL, style=Pango.Style.NORMAL, scale: float = 1.0):
        super().__init__()

        self.__weight = weight
        self.__style = style
        self.__scale = scale
        self.set_text(text)

    def set_text(self, text: str):
        markup = f'<span font_size="{int(self.__scale * 10 * 1024)}" ' \
                 f'font_weight="{int(self.__weight)}" ' \
                 f'font_style="{self._STYLES[self.__style]}">{GLib.markup_escape_text(text)}</span>'
        self.set_markup(markup)


class BoldLabel(FormattedLabel):
    """
    A FormattedLabel that is always bold and otherwise normal
    """

    def __init__(self, text=''):
        super().__init__(text=text, weight=Pango.Weight.BOLD)
