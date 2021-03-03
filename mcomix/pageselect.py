# -*- coding: utf-8 -*-

"""pageselect.py - The dialog window for the page selector"""

from gi.repository import Gtk

from mcomix.lib.callback import Callback
from mcomix.lib.mt import GlobalThreadPool
from mcomix.preferences import config


class Pageselector(Gtk.Dialog):
    """
    The Pageselector takes care of the popup page selector
    """

    def __init__(self, window):
        self.__window = window

        super().__init__(title='Go to page...', modal=True, destroy_with_parent=True)

        self.set_transient_for(window)

        self.add_buttons('_Go', Gtk.ResponseType.OK, '_Cancel', Gtk.ResponseType.CANCEL, )
        self.set_default_response(Gtk.ResponseType.OK)
        self.connect('response', self._response)
        self.set_resizable(True)

        self.__number_of_pages = self.__window.imagehandler.get_number_of_pages()

        self.__selector_adjustment = Gtk.Adjustment(value=self.__window.imagehandler.get_current_page(),
                                                    lower=1, upper=self.__number_of_pages,
                                                    step_increment=1, page_increment=1)

        self.__page_selector = Gtk.Scale.new(Gtk.Orientation.VERTICAL, self.__selector_adjustment)
        self.__page_selector.set_draw_value(False)
        self.__page_selector.set_digits(0)

        self.__page_spinner = Gtk.SpinButton.new(self.__selector_adjustment, 0.0, 0)
        self.__page_spinner.connect('changed', self._page_text_changed)
        self.__page_spinner.set_activates_default(True)
        self.__page_spinner.set_numeric(True)
        self.__pages_label = Gtk.Label(label=f' of {self.__number_of_pages}')
        self.__pages_label.set_alignment(0, 0.5)

        self.__image_preview = Gtk.Image()
        self.__image_preview.set_size_request(config['THUMBNAIL_SIZE'], config['THUMBNAIL_SIZE'])

        self.connect('configure-event', self._size_changed_cb)
        self.set_size_request(config['PAGESELECTOR_WIDTH'], config['PAGESELECTOR_HEIGHT'])

        # Group preview image and page selector next to each other
        preview_box = Gtk.HBox()
        preview_box.set_border_width(5)
        preview_box.set_spacing(5)
        preview_box.pack_start(self.__image_preview, True, True, 0)
        preview_box.pack_end(self.__page_selector, False, True, 0)
        # Below them, group selection spinner and current page label
        selection_box = Gtk.HBox()
        selection_box.set_border_width(5)
        selection_box.pack_start(self.__page_spinner, True, True, 0)
        selection_box.pack_end(self.__pages_label, False, True, 0)

        self.get_content_area().pack_start(preview_box, True, True, 0)
        self.get_content_area().pack_end(selection_box, False, True, 0)
        self.show_all()

        self.__selector_adjustment.connect('value-changed', self._cb_value_changed)

        # Set focus on the input box.
        self.__page_spinner.select_region(0, -1)
        self.__page_spinner.grab_focus()

        # Currently displayed thumbnail page.
        self.__thumbnail_page = 0
        self.__threadpool = GlobalThreadPool.threadpool
        self._update_thumbnail(int(self.__selector_adjustment.props.value))
        self.__window.imagehandler.page_available += self._page_available

    def _cb_value_changed(self, *args):
        """
        Called whenever the spinbox value changes. Updates the preview thumbnail
        """

        page = int(self.__selector_adjustment.props.value)
        if page != self.__thumbnail_page:
            self._update_thumbnail(page)

    def _size_changed_cb(self, *args):
        # Window cannot be scaled down unless the size request is reset
        self.set_size_request(-1, -1)
        # Store dialog size
        config['PAGESELECTOR_WIDTH'] = self.get_allocation().width
        config['PAGESELECTOR_HEIGHT'] = self.get_allocation().height

        self._update_thumbnail(int(self.__selector_adjustment.props.value))

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

        self.__window.imagehandler.page_available -= self._page_available
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

        return page, self.__window.imagehandler.get_thumbnail(page, size=(width, height), nowait=True)

    def _generate_thumbnail_cb(self, params):
        page, pixbuf = params
        return self._thumbnail_finished(page, pixbuf)

    @Callback
    def _thumbnail_finished(self, page: int, pixbuf):
        # Don't bother if we changed page in the meantime.
        if page == self.__thumbnail_page:
            self.__image_preview.set_from_pixbuf(pixbuf)

    def _page_available(self, page: int):
        if page == int(self.__selector_adjustment.props.value):
            self._update_thumbnail(page)
