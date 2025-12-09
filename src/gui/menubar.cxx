/**
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include "gui/menubar.hxx"

gui::menubar::menubar()
{
    auto menu = Gio::Menu::create();

    { // "File"
        auto section_1 = Gio::Menu::create();
        section_1->append("Open", "app.open");

        auto section_2 = Gio::Menu::create();
        section_2->append("Save Page As", "app.page_extract");
        section_2->append("Refresh", "app.refresh");
        section_2->append("Properties", "app.properties");

        auto section_3 = Gio::Menu::create();
        section_3->append("Trash", "app.trash");

        auto section_4 = Gio::Menu::create();
        section_4->append("Minimize", "app.minimize");
        section_4->append("Close", "app.close");
        section_4->append("Quit", "app.quit");

        auto file_menu = Gio::Menu::create();
        file_menu->append_section(section_1);
        file_menu->append_section(section_2);
        file_menu->append_section(section_3);
        file_menu->append_section(section_4);
        menu->append_submenu("File", file_menu);
    }

    { // "Edit"
        auto edit_menu = Gio::Menu::create();
        edit_menu->append("Keybindings", "app.keybindings");
        edit_menu->append("Preferences", "app.preferences");
        menu->append_submenu("Edit", edit_menu);
    }

    { // "View"
        auto view_menu = Gio::Menu::create();
        view_menu->append("Toggle Thumbnail Sidebar", "app.toggle_thumbar");
        view_menu->append("Toggle Menubar", "app.toggle_menubar");
        view_menu->append("Toggle Statusbar", "app.toggle_statusbar");
        view_menu->append("Toggle Center Spacing", "app.page_center_space");
        menu->append_submenu("View", view_menu);
    }

    { // "Navigation"
        auto section_1 = Gio::Menu::create();
        section_1->append("Next Page", "app.page_next");
        section_1->append("Previous Page", "app.page_prev");
        section_1->append("Single Step Next Page", "app.page_next_single");
        section_1->append("Single Step Previous Page", "app.page_prev_single");
        section_1->append("Fast Forward Next Page", "app.page_next_ff");
        section_1->append("Fast Forward Previous Page", "app.page_prev_ff");
        section_1->append("First Page", "app.page_first");
        section_1->append("Last Page", "app.page_last");

        auto section_2 = Gio::Menu::create();
        section_2->append("Page Selector", "app.page_select");

        auto section_3 = Gio::Menu::create();
        section_3->append("Next Archive", "app.archive_next");
        section_3->append("Previous Archive", "app.archive_prev");

        auto section_4 = Gio::Menu::create();
        section_4->append("First Archive", "app.archive_first");
        section_4->append("Last Archive", "app.archive_last");

        auto nav_menu = Gio::Menu::create();
        nav_menu->append_section(section_1);
        nav_menu->append_section(section_2);
        nav_menu->append_section(section_3);
        nav_menu->append_section(section_4);
        menu->append_submenu("Navigation", nav_menu);
    }

    { // "Bookmarks"
        auto book_menu = Gio::Menu::create();
        book_menu->append("Add Bookmark", "app.bookmark_add");
        book_menu->append("Open Bookmark Manager", "app.bookmark_manager");
        menu->append_submenu("Bookmarks", book_menu);
    }

    { // "Tools"
        auto tools_menu = Gio::Menu::create();
        tools_menu->append("Reset Rotation", "app.rotate_reset");
        tools_menu->append("Rotate 90°", "app.rotate_90");
        tools_menu->append("Rotate 180°", "app.rotate_180");
        tools_menu->append("Rotate 270°", "app.rotate_270");
        menu->append_submenu("Tools", tools_menu);
    }

    { // "Help"
        auto help_menu = Gio::Menu::create();
        help_menu->append("About", "app.about");
        help_menu->append("Donate", "app.donate");
        menu->append_submenu("Help", help_menu);
    }

    this->set_menu_model(menu);
}
