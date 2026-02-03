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

gui::menubar::menubar() noexcept
{
    auto menu = Gio::Menu::create();
    menu->append_submenu("File", create_file());
    menu->append_submenu("Edit", create_edit());
    menu->append_submenu("View", create_view());
    menu->append_submenu("Navigation", create_navigation());
    menu->append_submenu("Bookmarks", create_bookmarks());
    menu->append_submenu("Tools", create_tools());
    menu->append_submenu("Help", create_help());

    this->set_menu_model(menu);
}

Glib::RefPtr<Gio::Menu>
gui::menubar::create_file() noexcept
{
    auto menu = Gio::Menu::create();
    Glib::RefPtr<Gio::MenuItem> item;

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("Open", "app.open");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Control>O"));
        section->append_item(item);

        item = Gio::MenuItem::create("Close", "app.close");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Control>W"));
        section->append_item(item);

        menu->append_section(section);
    }

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("Save Page As", "app.page_extract");
        item->set_attribute_value("accel",
                                  Glib::Variant<Glib::ustring>::create("<Shift><Control>S"));
        section->append_item(item);

        item = Gio::MenuItem::create("Refresh", "app.refresh");
        item->set_attribute_value("accel",
                                  Glib::Variant<Glib::ustring>::create("<Shift><Control>R"));
        section->append_item(item);

        item = Gio::MenuItem::create("Properties", "app.properties");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Alt>Return"));
        section->append_item(item);

        menu->append_section(section);
    }

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("Trash", "app.trash");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("Delete"));
        section->append_item(item);

        menu->append_section(section);
    }

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("Exit", "app.exit");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Control>Q"));
        section->append_item(item);

        menu->append_section(section);
    }

    return menu;
}

Glib::RefPtr<Gio::Menu>
gui::menubar::create_edit() noexcept
{
    auto menu = Gio::Menu::create();
    Glib::RefPtr<Gio::MenuItem> item;

    menu->append("Keybindings", "app.keybindings");

    item = Gio::MenuItem::create("Preferences", "app.preferences");
    item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("F12"));
    menu->append_item(item);

    return menu;
}
Glib::RefPtr<Gio::Menu>
gui::menubar::create_view() noexcept
{
    auto menu = Gio::Menu::create();
    Glib::RefPtr<Gio::MenuItem> item;

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("Toggle Double Page", "app.view_double");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("D"));
        section->append_item(item);

        item = Gio::MenuItem::create("Toggle Manga Mode", "app.view_manga");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("M"));
        section->append_item(item);

        menu->append_section(section);
    }

    {
        auto section = Gio::Menu::create();

        section->append("Toggle Thumbnail Sidebar", "app.toggle_thumbar");
        section->append("Toggle Menubar", "app.toggle_menubar");
        section->append("Toggle Statusbar", "app.toggle_statusbar");

        item = Gio::MenuItem::create("Toggle Center Spacing", "app.page_center_space");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Shift>D"));
        section->append_item(item);

        menu->append_section(section);
    }

    return menu;
}
Glib::RefPtr<Gio::Menu>
gui::menubar::create_navigation() noexcept
{
    auto menu = Gio::Menu::create();
    Glib::RefPtr<Gio::MenuItem> item;

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("Next Page", "app.page_next");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("Down"));
        section->append_item(item);

        item = Gio::MenuItem::create("Previous Page", "app.page_prev");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("Up"));
        section->append_item(item);

        menu->append_section(section);
    }

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("Single Step Next Page", "app.page_next_single");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Control>Down"));
        section->append_item(item);

        item = Gio::MenuItem::create("Single Step Previous Page", "app.page_prev_single");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Control>Up"));
        section->append_item(item);

        menu->append_section(section);
    }

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("Fast Forward Next Page", "app.page_next_ff");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Shift>Down"));
        section->append_item(item);

        item = Gio::MenuItem::create("Fast Forward Previous Page", "app.page_prev_ff");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Shift>Up"));
        section->append_item(item);

        menu->append_section(section);
    }

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("First Page", "app.page_first");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("Home"));
        section->append_item(item);

        item = Gio::MenuItem::create("Last Page", "app.page_last");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("End"));
        section->append_item(item);

        menu->append_section(section);
    }

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("Page Selector", "app.page_select");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("G"));
        section->append_item(item);

        menu->append_section(section);
    }

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("Next Archive", "app.archive_next");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Control>Right"));
        section->append_item(item);

        item = Gio::MenuItem::create("Previous Archive", "app.archive_prev");
        item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Control>Left"));
        section->append_item(item);

        menu->append_section(section);
    }

    {
        auto section = Gio::Menu::create();

        item = Gio::MenuItem::create("First Archive", "app.archive_first");
        item->set_attribute_value("accel",
                                  Glib::Variant<Glib::ustring>::create("<Shift><Control>Left"));
        section->append_item(item);

        item = Gio::MenuItem::create("Last Archive", "app.archive_last");
        item->set_attribute_value("accel",
                                  Glib::Variant<Glib::ustring>::create("<Shift><Control>Right"));
        section->append_item(item);

        menu->append_section(section);
    }

    return menu;
}

Glib::RefPtr<Gio::Menu>
gui::menubar::create_bookmarks() noexcept
{
    auto menu = Gio::Menu::create();
    Glib::RefPtr<Gio::MenuItem> item;

    item = Gio::MenuItem::create("Add Bookmark", "app.bookmark_add");
    item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Control>D"));
    menu->append_item(item);

    item = Gio::MenuItem::create("Open Bookmark Manager", "app.bookmark_manager");
    item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Shift><Control>O"));
    menu->append_item(item);

    return menu;
}

Glib::RefPtr<Gio::Menu>
gui::menubar::create_tools() noexcept
{
    auto menu = Gio::Menu::create();
    Glib::RefPtr<Gio::MenuItem> item;

    menu->append("Reset Rotation", "app.rotate_reset");

    item = Gio::MenuItem::create("Rotate 90°", "app.rotate_90");
    item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("R"));
    menu->append_item(item);

    item = Gio::MenuItem::create("Rotate 180°", "app.rotate_180");
    item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Shift>R"));
    menu->append_item(item);

    item = Gio::MenuItem::create("Rotate 270°", "app.rotate_270");
    item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("<Control>R"));
    menu->append_item(item);

    return menu;
}

Glib::RefPtr<Gio::Menu>
gui::menubar::create_help() noexcept
{
    auto menu = Gio::Menu::create();
    Glib::RefPtr<Gio::MenuItem> item;

    item = Gio::MenuItem::create("About", "app.about");
    item->set_attribute_value("accel", Glib::Variant<Glib::ustring>::create("F1"));
    menu->append_item(item);

    menu->append("Donate", "app.donate");

    return menu;
}
