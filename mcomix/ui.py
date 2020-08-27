# -*- coding: utf-8 -*-

"""ui.py - UI definitions for main window"""

from gi.repository import Gtk

from mcomix import constants
from mcomix.bookmark_menu import BookmarksMenu
from mcomix.dialog_handler import DialogHandler
from mcomix.enhance_dialog import EnhanceDialog
from mcomix.preferences import prefs
from mcomix.preferences_dialog import PreferenceDialog


class MainUI(Gtk.UIManager):
    def __init__(self, window):
        super().__init__()

        self.__window = window

        def _action_lambda(fn, *args):
            return lambda *_: fn(*args)

        # ----------------------------------------------------------------
        # Create actions for the menus.
        # ----------------------------------------------------------------
        self.__actiongroup = Gtk.ActionGroup(name='mcomix-main')
        self.__actiongroup.add_actions([
            ('delete', Gtk.STOCK_DELETE, '_Delete',
             None, None, _action_lambda(window.move_file, 'delete')),
            ('refresh_archive', Gtk.STOCK_REFRESH, 'Re_fresh',
             None, None, window.filehandler.refresh_file),
            ('zoom_in', Gtk.STOCK_ZOOM_IN, 'Zoom _In',
             None, None, window.manual_zoom_in),
            ('zoom_out', Gtk.STOCK_ZOOM_OUT, 'Zoom _Out',
             None, None, window.manual_zoom_out),
            ('zoom_original', Gtk.STOCK_ZOOM_100, '_Normal Size',
             None, None, window.manual_zoom_original),
            ('minimize', Gtk.STOCK_LEAVE_FULLSCREEN, 'Mi_nimize',
             None, None, window.minimize),
            ('close', Gtk.STOCK_CLOSE, '_Close',
             None, None, _action_lambda(window.filehandler.close_file)),
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
            ('menu_bookmarks', None, '_Bookmarks'),
            ('menu_toolbars', None, 'T_oolbars'),
            ('menu_edit', None, '_Edit'),
            ('menu_open_with', Gtk.STOCK_OPEN, 'Open _with', ''),
            ('menu_file', None, '_File'),
            ('menu_view', None, '_View'),
            ('menu_tools', None, '_Tools'),
            ('menu_help', None, '_Help'),
            ('menu_transform', 'mcomix-transform', '_Transform image'),
            ('menu_autorotate', None, '_Auto-rotate image'),
            ('menu_autorotate_width', None, '...when width exceeds height'),
            ('menu_autorotate_height', None, '...when height exceeds width'),
            ('expander', None, None, None, None, None)])

        self.__actiongroup.add_toggle_actions([
            ('fullscreen', Gtk.STOCK_FULLSCREEN, '_Fullscreen',
             None, None, window.change_fullscreen),
            ('double_page', 'mcomix-double-page', '_Double page mode',
             None, None, window.change_double_page),
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
             None, None, window.change_manga_mode),
            ('keep_transformation', None, '_Keep transformation',
             None, None, window.change_keep_transformation),
            ('lens', 'mcomix-lens', 'Magnifying _lens',
             None, None, window.lens.toggle),
            ('stretch', None, 'Stretch small images',
             None, None, window.change_stretch)])

        # Note: Don't change the default value for the radio buttons unless
        # also fixing the code for setting the correct one on start-up in main.py.
        self.__actiongroup.add_radio_actions([
            ('best_fit_mode', 'mcomix-fitbest', '_Best fit mode',
             None, None, constants.ZOOM_MODE_BEST),
            ('fit_width_mode', 'mcomix-fitwidth', 'Fit _width mode',
             None, None, constants.ZOOM_MODE_WIDTH),
            ('fit_height_mode', 'mcomix-fitheight', 'Fit _height mode',
             None, None, constants.ZOOM_MODE_HEIGHT),
            ('fit_size_mode', 'mcomix-fitsize', 'Fit _size mode',
             None, None, constants.ZOOM_MODE_SIZE),
            ('fit_manual_mode', 'mcomix-fitmanual', 'M_anual zoom mode',
             None, None, constants.ZOOM_MODE_MANUAL)], 3, window.change_zoom_mode)

        # Automatically rotate image if width>height or height>width
        self.__actiongroup.add_radio_actions([
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

        self.__actiongroup.add_actions([
            ('about', Gtk.STOCK_ABOUT, '_About',
             None, None, DialogHandler.open_dialog)], (window, 'about-dialog'))

        self.__actiongroup.add_actions([
            ('properties', Gtk.STOCK_PROPERTIES, 'Proper_ties',
             None, None, DialogHandler.open_dialog)], (window, 'properties-dialog'))

        self.__actiongroup.add_actions([
            ('preferences', Gtk.STOCK_PREFERENCES, 'Pr_eferences',
             None, None, PreferenceDialog.open_dialog)], window)

        # Some actions added separately since they need extra arguments.
        self.__actiongroup.add_actions([
            ('enhance_image', 'mcomix-enhance-image', 'En_hance image...',
             None, None, EnhanceDialog.open_dialog)], window)

        # fix some gtk magic: removing unreqired accelerators
        Gtk.AccelMap.change_entry('<Actions>/mcomix-main/close', 0, 0, True)

        ui_description = """
        <ui>
            <menubar name="Menu">
                <menu action="menu_file">
                    <menuitem action="extract_page"/>
                    <menuitem action="refresh_archive"/>
                    <menuitem action="properties"/>
                    <separator/>
                    <menu action="menu_open_with"></menu>
                    <separator/>
                    <menuitem action="delete"/>
                    <separator/>
                    <menuitem action="minimize"/>
                    <menuitem action="close"/>
                    <menuitem action="quit"/>
                </menu>
                <menu action="menu_edit">
                    <menuitem action="preferences"/>
                </menu>
                <menu action="menu_view">
                    <menuitem action="fullscreen"/>
                    <menuitem action="double_page"/>
                    <menuitem action="manga_mode"/>
                    <separator/>
                    <menuitem action="best_fit_mode"/>
                    <menuitem action="fit_width_mode"/>
                    <menuitem action="fit_height_mode"/>
                    <menuitem action="fit_size_mode"/>
                    <menuitem action="fit_manual_mode"/>
                    <separator/>
                    <menuitem action="stretch"/>
                    <menuitem action="lens"/>
                    <menu action="menu_zoom">
                        <menuitem action="zoom_in"/>
                        <menuitem action="zoom_out"/>
                        <menuitem action="zoom_original"/>
                    </menu>
                    <separator/>
                    <menu action="menu_toolbars">
                        <menuitem action="menubar"/>
                        <menuitem action="statusbar"/>
                        <menuitem action="scrollbar"/>
                        <menuitem action="thumbnails"/>
                        <separator/>
                        <menuitem action="hide_all"/>
                    </menu>
                </menu>
                <menu action="menu_bookmarks">
                </menu>
                <menu action="menu_tools">
                    <menuitem action="enhance_image"/>
                    <menu action="menu_transform">
                        <menuitem action="rotate_90"/>
                        <menuitem action="rotate_270"/>
                        <menuitem action="rotate_180"/>
                        <separator/>
                        <menu action="menu_autorotate">
                            <menuitem action="no_autorotation"/>
                            <separator/>
                            <menuitem action="menu_autorotate_height"/>
                            <separator/>
                            <menuitem action="rotate_90_height"/>
                            <menuitem action="rotate_270_height"/>
                            <separator/>
                            <menuitem action="menu_autorotate_width"/>
                            <separator/>
                            <menuitem action="rotate_90_width"/>
                            <menuitem action="rotate_270_width"/>
                        </menu>
                        <separator/>
                        <menuitem action="flip_horiz"/>
                        <menuitem action="flip_vert"/>
                        <separator/>
                        <menuitem action="keep_transformation"/>
                    </menu>
                </menu>
                <menu action="menu_help">
                    <menuitem action="about"/>
                </menu>
            </menubar>
        </ui>
        """

        self.add_ui_from_string(ui_description)
        self.insert_action_group(self.__actiongroup, 0)

        self.__bookmarks = BookmarksMenu(self, window)
        self.get_widget('/Menu/menu_bookmarks').set_submenu(self.__bookmarks)
        self.get_widget('/Menu/menu_bookmarks').show()

        window.add_accel_group(self.get_accel_group())
