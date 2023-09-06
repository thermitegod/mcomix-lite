# -*- coding: utf-8 -*-

"""pageselect.py - The dialog window for the page selector"""

from __future__ import annotations

from gi.repository import Gtk

from mcomix.image_handler import ImageHandler
from mcomix.lib.events import Events, EventType
from mcomix.lib.threadpool import GlobalThreadPool

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcomix.main_window import MainWindow


class Pageselector(Gtk.Dialog):
    """
    The Pageselector takes care of the popup page selector
    """

    def __init__(self, window: MainWindow):
        self.__window = window

        self.__events = Events()
        self.__events.add_event(EventType.PAGE_AVAILABLE, self._page_available)

        self.__image_handler = ImageHandler()

        super().__init__(title='Go to page...', modal=True, destroy_with_parent=True)

        self.set_modal(True)
        self.set_transient_for(window)
        self.set_size_request(560, 820)

        self.add_buttons('_Go', Gtk.ResponseType.OK)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)

        self.set_default_response(Gtk.ResponseType.OK)
        self.connect('response', self._response)
        self.set_resizable(True)

        self.__number_of_pages = self.__image_handler.get_number_of_pages()

        self.__selector_adjustment = Gtk.Adjustment(value=self.__image_handler.get_current_page(),
                                                    lower=1, upper=self.__number_of_pages,
                                                    step_increment=1, page_increment=1)

        page_selector = Gtk.Scale.new(Gtk.Orientation.VERTICAL, self.__selector_adjustment)
        page_selector.set_draw_value(False)
        page_selector.set_digits(0)

        page_spinner = Gtk.SpinButton.new(self.__selector_adjustment, 0.0, 0)
        page_spinner.connect('changed', self._page_text_changed)
        page_spinner.set_activates_default(True)
        page_spinner.set_numeric(True)

        pages_label = Gtk.Label(label=f' of {self.__number_of_pages}')
        pages_label.set_xalign(0.0)
        pages_label.set_yalign(0.5)

        self.__image_preview = Gtk.Image()

        # Group preview image and page selector next to each other
        preview_box = Gtk.HBox()
        preview_box.set_border_width(5)
        preview_box.set_spacing(5)
        preview_box.pack_start(self.__image_preview, True, True, 0)
        preview_box.pack_end(page_selector, False, True, 0)
        # Below them, group selection spinner and current page label
        selection_box = Gtk.HBox()
        selection_box.set_border_width(5)
        selection_box.pack_start(page_spinner, True, True, 0)
        selection_box.pack_end(pages_label, False, True, 0)

        self.get_content_area().pack_start(preview_box, True, True, 0)
        self.get_content_area().pack_end(selection_box, False, True, 0)
        self.show_all()

        self.__selector_adjustment.connect('value-changed', self._cb_value_changed)

        # Set focus on the input box.
        page_spinner.select_region(0, -1)
        page_spinner.grab_focus()

        # Currently displayed thumbnail page.
        self.__thumbnail_page = 0
        self.__threadpool = GlobalThreadPool().threadpool
        self._update_thumbnail(int(self.__selector_adjustment.props.value))

    def _cb_value_changed(self, *args):
        """
        Called whenever the spinbox value changes. Updates the preview thumbnail
        """

        page = int(self.__selector_adjustment.props.value)
        if page != self.__thumbnail_page:
            self._update_thumbnail(page)

    def _page_text_changed(self, control, *args):
        """
        Called when the page selector has been changed. Used to instantly update
        the preview thumbnail when entering page numbers by hand
        """

        if control.get_text().isdigit():
            page = int(control.get_text())
            if 0 < page <= self.__number_of_pages:
                control.set_value(page)

    def _response(self, widget, event, *args):
        if event == Gtk.ResponseType.OK:
            self.__window.set_page(int(self.__selector_adjustment.props.value))

        self.__events.remove_event(EventType.PAGE_AVAILABLE, self._page_available)
        self.__threadpool.renew()
        self.destroy()

    def _update_thumbnail(self, page: int):
        """
        Trigger a thumbnail update
        """

        width = self.__image_preview.get_allocation().width
        height = self.__image_preview.get_allocation().height
        self.__thumbnail_page = page
        self.__threadpool.apply_async(
            self._generate_thumbnail, args=(page, width, height),
            callback=self._generate_thumbnail_cb)

    def _generate_thumbnail(self, page: int, width: int, height: int):
        """
        Generate the preview thumbnail for the page selector.
        A transparent image will be used if the page is not yet available
        """

        return page, self.__image_handler.get_thumbnail(page=page, size=(width, height))

    def _generate_thumbnail_cb(self, params):
        page, pixbuf = params
        return self._thumbnail_finished(page, pixbuf)

    def _thumbnail_finished(self, page: int, pixbuf):
        # Don't bother if we changed page in the meantime.
        if page == self.__thumbnail_page:
            self.__image_preview.set_from_pixbuf(pixbuf)

    def _page_available(self, page: int):
        if page == int(self.__selector_adjustment.props.value):
            self._update_thumbnail(page)
