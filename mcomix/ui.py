# -*- coding: utf-8 -*-

"""ui.py - UI definitions for main window"""

from gi.repository import Gtk

from mcomix import bookmark_menu, constants, dialog_handler, enhance_dialog, file_chooser_main_dialog, \
    openwith_menu, preferences_dialog, status
from mcomix.preferences import prefs


class MainUI(Gtk.UIManager):
    def __init__(self, window):
        super(MainUI, self).__init__()

        self._window = window
        self._tooltipstatus = status.TooltipStatusHelper(self, window.statusbar)

        def _action_lambda(fn, *args):
            return lambda *_: fn(*args)

        # ----------------------------------------------------------------
        # Create actions for the menus.
        # ----------------------------------------------------------------
        self._actiongroup = Gtk.ActionGroup(name='mcomix-main')
        self._actiongroup.add_actions([
            ('delete', Gtk.STOCK_DELETE, '_Delete',
             None, 'Deletes the current file or archive from disk.',
             window.delete),
            ('next_page', Gtk.STOCK_GO_FORWARD, '_Next page',
             None, 'Next page', _action_lambda(window.flip_page, +1)),
            ('previous_page', Gtk.STOCK_GO_BACK, '_Previous page',
             None, 'Previous page', _action_lambda(window.flip_page, -1)),
            ('first_page', Gtk.STOCK_GOTO_FIRST, '_First page',
             None, 'First page', _action_lambda(window.first_page)),
            ('last_page', Gtk.STOCK_GOTO_LAST, '_Last page',
             None, 'Last page', _action_lambda(window.last_page)),
            ('go_to', Gtk.STOCK_JUMP_TO, '_Go to page...',
             None, 'Go to page...', window.page_select),
            ('refresh_archive', Gtk.STOCK_REFRESH, 'Re_fresh',
             None, 'Reloads the currently opened files or archive.',
             window.filehandler.refresh_file),
            ('next_archive', Gtk.STOCK_MEDIA_NEXT, 'Next _archive',
             None, 'Next archive', window.filehandler._open_next_archive),
            ('previous_archive', Gtk.STOCK_MEDIA_PREVIOUS, 'Previous a_rchive',
             None, 'Previous archive', window.filehandler._open_previous_archive),
            ('next_directory', Gtk.STOCK_REDO, 'Next directory',
             None, 'Next directory', window.filehandler.open_next_directory),
            ('previous_directory', Gtk.STOCK_UNDO, 'Previous directory',
             None, 'Previous directory', window.filehandler.open_previous_directory),
            ('zoom_in', Gtk.STOCK_ZOOM_IN, 'Zoom _In',
             None, None, window.manual_zoom_in),
            ('zoom_out', Gtk.STOCK_ZOOM_OUT, 'Zoom _Out',
             None, None, window.manual_zoom_out),
            ('zoom_original', Gtk.STOCK_ZOOM_100, '_Normal Size',
             None, None, window.manual_zoom_original),
            ('minimize', Gtk.STOCK_LEAVE_FULLSCREEN, 'Mi_nimize',
             None, None, window.minimize),
            ('close', Gtk.STOCK_CLOSE, '_Close',
             None, 'Closes all opened files.', _action_lambda(window.filehandler.close_file)),
            ('quit', Gtk.STOCK_QUIT, '_Quit',
             None, None, window.terminate_program),
            ('rotate_90', 'mcomix-rotate-90', '_Rotate 90 degrees CW',
             None, None, window.rotate_90),
            ('rotate_180', 'mcomix-rotate-180', 'Rotate 180 de_grees',
             None, None, window.rotate_180),
            ('rotate_270', 'mcomix-rotate-270', 'Rotat_e 90 degrees CCW',
             None, None, window.rotate_270),
            ('flip_horiz', 'mcomix-flip-horizontal', 'Fli_p horizontally',
             None, None, window.flip_horizontally),
            ('flip_vert', 'mcomix-flip-vertical', 'Flip _vertically',
             None, None, window.flip_vertically),
            ('extract_page', Gtk.STOCK_SAVE_AS, 'Save _As',
             None, None, window.extract_page),
            ('menu_zoom', 'mcomix-zoom', '_Zoom'),
            ('menu_bookmarks_popup', 'comix-add-bookmark', '_Bookmarks'),
            ('menu_bookmarks', None, '_Bookmarks'),
            ('menu_toolbars', None, 'T_oolbars'),
            ('menu_edit', None, '_Edit'),
            ('menu_open_with', Gtk.STOCK_OPEN, 'Open _with', ''),
            ('menu_open_with_popup', Gtk.STOCK_OPEN, 'Open _with', ''),
            ('menu_file', None, '_File'),
            ('menu_view', None, '_View'),
            ('menu_view_popup', 'comix-image', '_View'),
            ('menu_go', None, '_Go'),
            ('menu_go_popup', Gtk.STOCK_GO_FORWARD, '_Go'),
            ('menu_tools', None, '_Tools'),
            ('menu_help', None, '_Help'),
            ('menu_transform', 'mcomix-transform', '_Transform image'),
            ('menu_autorotate', None, '_Auto-rotate image'),
            ('menu_autorotate_width', None, '...when width exceeds height'),
            ('menu_autorotate_height', None, '...when height exceeds width'),
            ('expander', None, None, None, None, None)])

        self._actiongroup.add_toggle_actions([
            ('fullscreen', Gtk.STOCK_FULLSCREEN, '_Fullscreen',
             None, 'Fullscreen mode', window.change_fullscreen),
            ('double_page', 'mcomix-double-page', '_Double page mode',
             None, 'Double page mode', window.change_double_page),
            ('toolbar', None, '_Toolbar',
             None, None, window.change_toolbar_visibility),
            ('menubar', None, '_Menubar',
             None, None, window.change_menubar_visibility),
            ('statusbar', None, 'St_atusbar',
             None, None, window.change_statusbar_visibility),
            ('scrollbar', None, 'S_crollbars',
             None, None, window.change_scrollbar_visibility),
            ('thumbnails', None, 'Th_umbnails',
             None, None, window.change_thumbnails_visibility),
            ('hide_all', None, 'H_ide all',
             None, None, window.change_hide_all),
            ('manga_mode', 'mcomix-manga', '_Manga mode',
             None, 'Manga mode', window.change_manga_mode),
            ('keep_transformation', None, '_Keep transformation',
             None, 'Keeps the currently selected transformation for the next pages.',
             window.change_keep_transformation),
            ('lens', 'mcomix-lens', 'Magnifying _lens',
             None, 'Magnifying lens', window.lens.toggle),
            ('stretch', None, 'Stretch small images',
             None, 'Stretch images to fit to the screen, depending on zoom mode.',
             window.change_stretch)])

        # Note: Don't change the default value for the radio buttons unless
        # also fixing the code for setting the correct one on start-up in main.py.
        self._actiongroup.add_radio_actions([
            ('best_fit_mode', 'mcomix-fitbest', '_Best fit mode',
             None, 'Best fit mode', constants.ZOOM_MODE_BEST),
            ('fit_width_mode', 'mcomix-fitwidth', 'Fit _width mode',
             None, 'Fit width mode', constants.ZOOM_MODE_WIDTH),
            ('fit_height_mode', 'mcomix-fitheight', 'Fit _height mode',
             None, 'Fit height mode', constants.ZOOM_MODE_HEIGHT),
            ('fit_size_mode', 'mcomix-fitsize', 'Fit _size mode',
             None, 'Fit to size mode', constants.ZOOM_MODE_SIZE),
            ('fit_manual_mode', 'mcomix-fitmanual', 'M_anual zoom mode',
             None, 'Manual zoom mode', constants.ZOOM_MODE_MANUAL)],
                3, window.change_zoom_mode)

        # Automatically rotate image if width>height or height>width
        self._actiongroup.add_radio_actions([
            ('no_autorotation', None, 'Never',
             None, None, constants.AUTOROTATE_NEVER),
            ('rotate_90_width', 'mcomix-rotate-90', '_Rotate 90 degrees CW',
             None, None, constants.AUTOROTATE_WIDTH_90),
            ('rotate_270_width', 'mcomix-rotate-270', 'Rotat_e 90 degrees CCW',
             None, None, constants.AUTOROTATE_WIDTH_270),
            ('rotate_90_height', 'mcomix-rotate-90', '_Rotate 90 degrees CW',
             None, None, constants.AUTOROTATE_HEIGHT_90),
            ('rotate_270_height', 'mcomix-rotate-270', 'Rotat_e 90 degrees CCW',
             None, None, constants.AUTOROTATE_HEIGHT_270)],
                prefs['auto rotate depending on size'], window.change_autorotation)

        self._actiongroup.add_actions([
            ('about', Gtk.STOCK_ABOUT, '_About',
             None, None, dialog_handler.open_dialog)], (window, 'about-dialog'))

        self._actiongroup.add_actions([
            ('properties', Gtk.STOCK_PROPERTIES, 'Proper_ties',
             None, None, dialog_handler.open_dialog)], (window, 'properties-dialog'))

        self._actiongroup.add_actions([
            ('preferences', Gtk.STOCK_PREFERENCES, 'Pr_eferences',
             None, None, preferences_dialog.open_dialog)], window)

        # Some actions added separately since they need extra arguments.
        self._actiongroup.add_actions([
            ('open', Gtk.STOCK_OPEN, '_Open...',
             None, None, file_chooser_main_dialog.open_main_filechooser_dialog),
            ('enhance_image', 'mcomix-enhance-image', 'En_hance image...',
             None, None, enhance_dialog.open_dialog)], window)

        # fix some gtk magic: removing unreqired accelerators
        Gtk.AccelMap.change_entry(f'<Actions>/mcomix-main/{"close"}', 0, 0, True)

        ui_description = """
        <ui>
            <toolbar name="Tool">
                <toolitem action="previous_archive" />
                <toolitem action="first_page" />
                <toolitem action="previous_page" />
                <toolitem action="go_to" />
                <toolitem action="next_page" />
                <toolitem action="last_page" />
                <toolitem action="next_archive" />
                <separator />
                <toolitem action="fullscreen" />
                <toolitem action="expander" />
                <toolitem action="best_fit_mode" />
                <toolitem action="fit_width_mode" />
                <toolitem action="fit_height_mode" />
                <toolitem action="fit_size_mode" />
                <toolitem action="fit_manual_mode" />
                <separator />
                <toolitem action="double_page" />
                <toolitem action="manga_mode" />
                <separator />
                <toolitem action="lens" />
            </toolbar>

            <menubar name="Menu">
                <menu action="menu_file">
                    <menuitem action="open" />
                    <separator />
                    <menuitem action="extract_page" />
                    <menuitem action="refresh_archive" />
                    <menuitem action="properties" />
                    <separator />
                    <menu action="menu_open_with"></menu>
                    <separator />
                    <menuitem action="delete" />
                    <separator />
                    <menuitem action="minimize" />
                    <menuitem action="close" />
                    <menuitem action="quit" />
                </menu>
                <menu action="menu_edit">
                    <menuitem action="preferences" />
                </menu>
                <menu action="menu_view">
                    <menuitem action="fullscreen" />
                    <menuitem action="double_page" />
                    <menuitem action="manga_mode" />
                    <separator />
                    <menuitem action="best_fit_mode" />
                    <menuitem action="fit_width_mode" />
                    <menuitem action="fit_height_mode" />
                    <menuitem action="fit_size_mode" />
                    <menuitem action="fit_manual_mode" />
                    <separator />
                    <menuitem action="stretch" />
                    <menuitem action="lens" />
                    <menu action="menu_zoom">
                        <menuitem action="zoom_in" />
                        <menuitem action="zoom_out" />
                        <menuitem action="zoom_original" />
                    </menu>
                    <separator />
                    <menu action="menu_toolbars">
                        <menuitem action="menubar" />
                        <menuitem action="toolbar" />
                        <menuitem action="statusbar" />
                        <menuitem action="scrollbar" />
                        <menuitem action="thumbnails" />
                        <separator />
                        <menuitem action="hide_all" />
                    </menu>
                </menu>
                <menu action="menu_go">
                    <menuitem action="next_page" />
                    <menuitem action="previous_page" />
                    <menuitem action="go_to" />
                    <menuitem action="first_page" />
                    <menuitem action="last_page" />
                    <separator />
                    <menuitem action="next_archive" />
                    <menuitem action="previous_archive" />
                    <separator />
                    <menuitem action="next_directory" />
                    <menuitem action="previous_directory" />
                </menu>
                <menu action="menu_bookmarks">
                </menu>
                <menu action="menu_tools">
                    <menuitem action="enhance_image" />
                    <menu action="menu_transform">
                        <menuitem action="rotate_90" />
                        <menuitem action="rotate_270" />
                        <menuitem action="rotate_180" />
                        <separator />
                        <menu action="menu_autorotate">
                            <menuitem action="no_autorotation" />
                            <separator />
                            <menuitem action="menu_autorotate_height" />
                            <separator />
                            <menuitem action="rotate_90_height" />
                            <menuitem action="rotate_270_height" />
                            <separator />
                            <menuitem action="menu_autorotate_width" />
                            <separator />
                            <menuitem action="rotate_90_width" />
                            <menuitem action="rotate_270_width" />
                        </menu>
                        <separator />
                        <menuitem action="flip_horiz" />
                        <menuitem action="flip_vert" />
                        <separator />
                        <menuitem action="keep_transformation" />
                    </menu>
                </menu>
                <menu action="menu_help">
                    <menuitem action="about" />
                </menu>
            </menubar>

            <popup name="Popup">
                <menu action="menu_go_popup">
                    <menuitem action="next_page" />
                    <menuitem action="previous_page" />
                    <menuitem action="go_to" />
                    <menuitem action="first_page" />
                    <menuitem action="last_page" />
                    <separator />
                    <menuitem action="next_archive" />
                    <menuitem action="previous_archive" />
                    <separator />
                    <menuitem action="next_directory" />
                    <menuitem action="previous_directory" />
                </menu>
                <menu action="menu_view_popup">
                    <menuitem action="fullscreen" />
                    <menuitem action="double_page" />
                    <menuitem action="manga_mode" />
                    <separator />
                    <menuitem action="best_fit_mode" />
                    <menuitem action="fit_width_mode" />
                    <menuitem action="fit_height_mode" />
                    <menuitem action="fit_size_mode" />
                    <menuitem action="fit_manual_mode" />
                    <separator />
                    <menuitem action="enhance_image" />
                    <separator />
                    <menuitem action="stretch" />
                    <menuitem action="lens" />
                    <menu action="menu_zoom">
                        <menuitem action="zoom_in" />
                        <menuitem action="zoom_out" />
                        <menuitem action="zoom_original" />
                    </menu>
                    <separator />
                    <menu action="menu_toolbars">
                        <menuitem action="menubar" />
                        <menuitem action="toolbar" />
                        <menuitem action="statusbar" />
                        <menuitem action="scrollbar" />
                        <menuitem action="thumbnails" />
                        <separator />
                        <menuitem action="hide_all" />
                    </menu>
                </menu>
                <menu action="menu_bookmarks_popup">
                </menu>
                <separator />
                <menuitem action="open" />
                <separator />
                <menu action="menu_open_with_popup"></menu>
                <separator />
                <menuitem action="preferences" />
                <separator />
                <menuitem action="close" />
                <menuitem action="quit" />
            </popup>
        </ui>
        """

        self.add_ui_from_string(ui_description)
        self.insert_action_group(self._actiongroup, 0)

        self.bookmarks = bookmark_menu.BookmarksMenu(self, window)
        self.get_widget('/Menu/menu_bookmarks').set_submenu(self.bookmarks)
        self.get_widget('/Menu/menu_bookmarks').show()

        self.bookmarks_popup = bookmark_menu.BookmarksMenu(self, window)
        self.get_widget('/Popup/menu_bookmarks_popup').set_submenu(self.bookmarks_popup)
        self.get_widget('/Popup/menu_bookmarks_popup').show()

        openwith = openwith_menu.OpenWithMenu(self, window)
        self.get_widget('/Menu/menu_file/menu_open_with').set_submenu(openwith)
        self.get_widget('/Menu/menu_file/menu_open_with').show()
        openwith = openwith_menu.OpenWithMenu(self, window)
        self.get_widget('/Popup/menu_open_with_popup').set_submenu(openwith)
        self.get_widget('/Popup/menu_open_with_popup').show()

        window.add_accel_group(self.get_accel_group())

        # Is there no built-in way to do this?
        self.get_widget('/Tool/expander').set_expand(True)
        self.get_widget('/Tool/expander').set_sensitive(False)
