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

#include <algorithm>
#include <chrono>
#include <filesystem>
#include <format>
#include <optional>
#include <string>
#include <system_error>
#include <utility>

#include <cmath>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include <ztd/ztd.hxx>

#include "settings/config.hxx"

#include "gui/main-window.hxx"
#include "gui/statusbar.hxx"
#include "gui/thumbbar.hxx"

#include "gui/dialog/about.hxx"
#include "gui/dialog/bookmarks.hxx"
#include "gui/dialog/donate.hxx"
#include "gui/dialog/pageselect.hxx"
#include "gui/dialog/preferences.hxx"
#include "gui/dialog/properties.hxx"

#include "gui/lib/image-tools.hxx"

#include "vfs/trash-can.hxx"
#include "vfs/user-dirs.hxx"

#include "logger.hxx"
#include "types.hxx"

gui::main_window::main_window(const Glib::RefPtr<Gtk::Application>& app,
                              const std::vector<std::filesystem::path>& filelist)
{
    this->set_application(app);
    assert(this->get_application() != nullptr);

    this->set_title(PACKAGE_NAME_FANCY);
    this->set_size_request(500, 500);
    this->set_resizable(true);
    this->set_visible(true);

    config::load(vfs::program::config(), this->settings);

    this->bookmarks_->signal_load_error().connect(
        [this](std::string msg)
        {
            auto dialog = Gtk::AlertDialog::create("Bookmark Load Error");
            dialog->set_detail(msg);
            dialog->set_modal(true);
            dialog->show(*this);
        });
    this->bookmarks_->signal_save_error().connect(
        [this](std::string msg)
        {
            auto dialog = Gtk::AlertDialog::create("Bookmark Save Error");
            dialog->set_detail(msg);
            dialog->set_modal(true);
            dialog->show(*this);
        });
    this->bookmarks_->load();

    this->file_handler_->signal_file_opened().connect([this]() { this->on_file_opened(); });
    this->file_handler_->signal_file_closed().connect([this]() { this->on_file_closed(); });
    this->file_handler_->signal_page_available().connect([this](const page_t page)
                                                         { this->page_available(page); });
    this->file_handler_->signal_page_set().connect([this](const page_t page)
                                                   { this->set_page(page); });

    app->add_action("page_next", [this]() { this->flip_page(1); });
    app->add_action("page_prev", [this]() { this->flip_page(-1); });
    app->add_action("page_next_single", [this]() { this->flip_page(1, true); });
    app->add_action("page_prev_single", [this]() { this->flip_page(-1, true); });
    app->add_action("page_next_ff", [this]() { this->flip_page(this->settings->page_ff_step); });
    app->add_action("page_prev_ff", [this]() { this->flip_page(-this->settings->page_ff_step); });
    app->add_action("page_first", [this]() { this->first_page(); });
    app->add_action("page_last", [this]() { this->last_page(); });
    app->add_action("page_select", [this]() { this->on_open_page_select(); });

    app->add_action("archive_next",
                    [this]() { auto _ = this->file_handler_->open_next_archive(); });
    app->add_action("archive_prev",
                    [this]() { auto _ = this->file_handler_->open_prev_archive(); });

    app->add_action("rotate_reset",
                    [this]()
                    {
                        this->settings->rotation = 0;
                        this->rotate_x(0);
                    });
    app->add_action("rotate_90", [this]() { this->rotate_x(90); });
    app->add_action("rotate_180", [this]() { this->rotate_x(180); });
    app->add_action("rotate_270", [this]() { this->rotate_x(270); });

    app->add_action("bookmark_add", [this]() { this->on_bookmark_add(); });
    app->add_action("bookmark_manager", [this]() { this->on_bookmark_manager(); });

    app->add_action("view_double", [this]() { this->change_double_page(); });
    app->add_action("view_manga", [this]() { this->change_manga_mode(); });

    app->add_action("toggle_thumbar",
                    [this]()
                    {
                        this->settings->hide_thumbar = !this->settings->hide_thumbar;
                        this->thumb_sidebar_.set_visible(!this->settings->hide_thumbar);
                    });
    app->add_action("toggle_menubar",
                    [this]()
                    {
                        this->settings->hide_menubar = !this->settings->hide_menubar;
                        this->menubar_.set_visible(!this->settings->hide_menubar);
                    });
    app->add_action("toggle_statusbar",
                    [this]()
                    {
                        this->settings->hide_statusbar = !this->settings->hide_statusbar;
                        this->statusbar_.set_visible(!this->settings->hide_statusbar);
                    });
    app->add_action("page_center_space", [this]() { this->viewport_.toggle_page_padding(); });

    app->add_action("escape", [this]() { this->on_escape_event(); });
    app->add_action("fullscreen", [this]() { this->change_fullscreen(); });
    app->add_action("minimize", [this]() { this->minimize(); });

    app->add_action("close", [this]() { this->file_handler_->close_file(); });
    app->add_action("trash", [this]() { this->on_trash_current_file(); });
    app->add_action("move", [this]() { this->on_move_current_file(); });
    app->add_action("page_extract", [this]() { this->on_open_page_extractor(); });

    app->add_action("open", [this]() { this->on_open_filechooser(); });
    app->add_action("quit", [this]() { this->close(); });
    app->add_action("refresh", [this]() { this->file_handler_->refresh_opened(); });
    app->add_action("keybindings", [this]() { this->on_open_keybindings(); });
    app->add_action("preferences", [this]() { this->on_open_preferences(); });
    app->add_action("properties", [this]() { this->on_open_properties(); });
    app->add_action("donate", [this]() { this->on_open_donate(); });
    app->add_action("about", [this]() { this->on_open_about(); });

    this->add_shortcuts();

    this->view_state->set_manga_mode(this->settings->default_manga_mode);
    this->view_state->set_displaying_double(false);

    this->thumb_sidebar_.set_visible(false);
    this->thumb_sidebar_.signal_page_selected().connect([this](const auto page)
                                                        { this->set_page(page); });

    this->setup_menubar();

    this->box_.set_orientation(Gtk::Orientation::VERTICAL);
    this->box_.set_hexpand(true);
    this->box_.set_vexpand(true);

    this->box_.append(this->menubar_);

    this->center_box_.set_orientation(Gtk::Orientation::HORIZONTAL);
    this->center_box_.set_hexpand(true);
    this->center_box_.set_vexpand(true);
    this->box_.append(this->center_box_);

    this->center_box_.append(this->thumb_sidebar_);
    this->center_box_.append(this->viewport_);

    this->box_.append(this->statusbar_);

    this->set_child(this->box_);

    if (this->settings->hide_thumbar)
    {
        this->thumb_sidebar_.set_visible(false);
    }
    if (this->settings->hide_statusbar)
    {
        this->statusbar_.set_visible(false);
    }
    if (this->settings->hide_menubar)
    {
        this->menubar_.set_visible(false);
    }

    // Use idle signal to start filehandler otherwise the
    // window will not get displayed until after open_file_init()
    // has returned. This also causes other problems since the
    // window size will be '1x1' during the initial page draw.
    Glib::signal_idle().connect_once([this, filelist]()
                                     { this->file_handler_->open_file_init(filelist); });
}

gui::main_window::~main_window()
{
    config::save(vfs::program::config(), this->settings);

    this->file_handler_->close_file();
}

void
gui::main_window::setup_menubar() noexcept
{
    auto app = this->get_application();
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

    this->menubar_.set_menu_model(menu);
}

void
gui::main_window::add_shortcuts() noexcept
{
    auto controller = Gtk::ShortcutController::create();

    { // Quit
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->close();
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_q, Gdk::ModifierType::CONTROL_MASK),
            action));
    }

    // Navigation //

    { // Next Page
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.page_next");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Down), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Down), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Page_Down), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Page_Down), action));
    }

    { // Next Page Dynamic
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                if (this->view_state->is_manga_mode())
                {
                    this->activate_action("app.page_prev");
                }
                else
                {
                    this->activate_action("app.page_next");
                }
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Right), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Right), action));
    }

    { // Previous Page
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.page_prev");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Up), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Up), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Page_Up), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Page_Up), action));
    }

    { // Previous Page Dynamic
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                if (this->view_state->is_manga_mode())
                {
                    this->activate_action("app.page_next");
                }
                else
                {
                    this->activate_action("app.page_prev");
                }
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Left), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Left), action));
    }

    { // Next Page Singlestep
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.page_next_single");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_Down, Gdk::ModifierType::CONTROL_MASK),
            action));
        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_KP_Down, Gdk::ModifierType::CONTROL_MASK),
            action));
        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_Page_Down, Gdk::ModifierType::CONTROL_MASK),
            action));
        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_KP_Page_Down, Gdk::ModifierType::CONTROL_MASK),
            action));
    }

    { // Previous Page Singlestep
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.page_prev_single");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_Up, Gdk::ModifierType::CONTROL_MASK),
            action));
        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_KP_Up, Gdk::ModifierType::CONTROL_MASK),
            action));
        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_Page_Up, Gdk::ModifierType::CONTROL_MASK),
            action));
        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_KP_Page_Up, Gdk::ModifierType::CONTROL_MASK),
            action));
    }

    { // Next Page FF
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.page_next_ff");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_Down, Gdk::ModifierType::SHIFT_MASK),
            action));
    }

    { // Previous Page FF
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.page_prev_ff");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_Up, Gdk::ModifierType::SHIFT_MASK),
            action));
    }

    { // First Page
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.page_first");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Home), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Home), action));
    }

    { // Last Page
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.page_last");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_End), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_End), action));
    }

    { // Goto
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.page_select");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_g), action));
    }

    { // Next Archive
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.archive_next");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_Right, Gdk::ModifierType::CONTROL_MASK),
            action));
    }

    { // Previous Archive
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.archive_prev");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_Left, Gdk::ModifierType::CONTROL_MASK),
            action));
    }

    // View //
    { // Keep Transformation
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.keep_transformation");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_k), action));
    }

    { // Rotate 90
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.rotate_90");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_r), action));
    }

    { // Rotate 180
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.rotate_180");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_r, Gdk::ModifierType::SHIFT_MASK),
            action));
    }

    { // Rotate 270
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.rotate_270");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_r, Gdk::ModifierType::CONTROL_MASK),
            action));
    }

    // View Mode //

    { // Double Page
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.view_double");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_d), action));
    }

    { // Manga Mode
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.view_manga");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_m), action));
    }

    { // Toggle Douoble Page Center Spacing
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.page_center_space");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_D, Gdk::ModifierType::SHIFT_MASK),
            action));
    }

    // General UI //

    { // Exit / Exit Fullscreen
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.escape");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Escape), action));
    }

    { // Fullscreen
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.fullscreen");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_f), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_F11), action));
    }

    { // Minimize
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.minimize");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_m), action));
    }

    // Info //

    {
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.donate");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_F1, Gdk::ModifierType::CONTROL_MASK),
            action));
    }

    {
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.about");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_F1), action));
    }

    // File Operations //

    { // Close
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.close");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_w, Gdk::ModifierType::CONTROL_MASK),
            action));
    }

    { // Trash
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.trash");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Delete), action));
    }

    { // Extract Page
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.page_extract");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_s,
                                                             Gdk::ModifierType::CONTROL_MASK |
                                                                 Gdk::ModifierType::SHIFT_MASK),
                                  action));
    }

    { // Move File
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.move");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_grave), action));
    }

    { // Open
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.open");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_o, Gdk::ModifierType::CONTROL_MASK),
            action));
    }

    { // Preferences
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.preferences");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_F12), action));
    }

    { // Properties
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.properties");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_Return, Gdk::ModifierType::ALT_MASK),
            action));
    }

    { // Refresh Archive
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.refresh");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_r,
                                                             Gdk::ModifierType::CONTROL_MASK |
                                                                 Gdk::ModifierType::SHIFT_MASK),
                                  action));
    }

    { // Bookmark Add
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.bookmark_add");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_d, Gdk::ModifierType::CONTROL_MASK),
            action));
    }

    { //  Bookmark Manager
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                this->activate_action("app.bookmark_manager");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_O,
                                                             Gdk::ModifierType::CONTROL_MASK |
                                                                 Gdk::ModifierType::SHIFT_MASK),
                                  action));
    }

    this->add_controller(controller);
}

void
gui::main_window::on_bookmark_add() noexcept
{
    const auto image_handler = this->file_handler_->image_handler();

    this->bookmarks_->add({this->file_handler_->get_real_path(),
                           image_handler->get_current_page(),
                           image_handler->get_number_of_pages(),
                           std::chrono::system_clock::to_time_t(std::chrono::system_clock::now())});
}

void
gui::main_window::on_bookmark_manager() noexcept
{
    Gtk::make_managed<gui::dialog::bookmarks>(*this,
                                              this->file_handler_,
                                              this->bookmarks_,
                                              this->settings);
}

void
gui::main_window::on_open_page_extractor() noexcept
{
    const auto path = this->file_handler_->image_handler()->get_path_to_page();

    auto dialog = Gtk::FileDialog::create();

    dialog->set_title("Extract Image To");
    dialog->set_modal(true);
    dialog->set_initial_name(path.filename());
    dialog->set_initial_folder(Gio::File::create_for_path(vfs::user::home()));

    auto slot = [this, dialog, path](const Glib::RefPtr<Gio::AsyncResult>& result)
    {
        try
        {
            auto file = dialog->save_finish(result);
            if (!file)
            {
                return;
            }

            std::error_code ec;
            std::filesystem::copy_file(path, file->get_path(), ec);
            if (ec)
            {
                auto alert = Gtk::AlertDialog::create("Failed To Extract File!");
                alert->set_detail(std::format("From: {}\nTo:   {}\nReason: {}",
                                              path.string(),
                                              file->get_path(),
                                              ec.message()));
                alert->set_modal(true);
                alert->show(*this);
            }
        }
        catch (const Gtk::DialogError& err)
        {
            logger::error<logger::gui>("Gtk::FileDialog error: {}", err.what());
        }
        catch (const Glib::Error& err)
        {
            logger::error<logger::gui>("Unexpected exception: {}", err.what());
        }
    };
    dialog->save(*this, slot);
}

void
gui::main_window::on_open_filechooser() noexcept
{
    auto filter_image = Gtk::FileFilter::create();
    filter_image->set_name("All image files");
    filter_image->add_mime_type("image/*");

    auto filter_archive = Gtk::FileFilter::create();
    filter_archive->set_name("All archive files");
    // filter_archive->add_suffix("zip");
    filter_archive->add_mime_type("application/zip");
    filter_archive->add_mime_type("application/x-7z-compressed");
    filter_archive->add_mime_type("application/vnd.rar");
    filter_archive->add_mime_type("application/x-tar");

    auto dialog = Gtk::FileDialog::create();

    dialog->set_title("Open files");
    dialog->set_modal(true);

    auto filters = Gio::ListStore<Gtk::FileFilter>::create();
    filters->append(filter_image);
    filters->append(filter_archive);

    dialog->set_default_filter(filter_archive);
    dialog->set_filters(filters);

    const auto open_path = [this]()
    {
        std::filesystem::path path;
        if (this->file_handler_->is_file_loaded())
        {
            if (this->file_handler_->is_archive())
            {
                return this->file_handler_->get_base_path().parent_path();
            }
            else
            {
                return this->file_handler_->get_base_path();
            }
        }
        else
        {
            return vfs::user::home();
        }
    }();

    dialog->set_initial_folder(Gio::File::create_for_path(open_path));

    auto slot = [this, dialog](const Glib::RefPtr<Gio::AsyncResult>& result)
    {
        try
        {
            auto files = dialog->open_multiple_finish(result);
            if (files.empty())
            {
                return;
            }
            std::vector<std::filesystem::path> paths;
            for (const auto& file : files)
            {
                paths.push_back(file->get_path());
            }
            this->file_handler_->open_file_init(paths);
        }
        catch (const Gtk::DialogError& err)
        {
            logger::error<logger::gui>("Gtk::FileDialog error: {}", err.what());
        }
        catch (const Glib::Error& err)
        {
            logger::error<logger::gui>("Unexpected exception: {}", err.what());
        }
    };
    dialog->open_multiple(*this, slot);
}

void
gui::main_window::on_open_keybindings() noexcept
{
    auto dialog = Gtk::AlertDialog::create("Not Implemented");
    dialog->set_detail("gui::main_window::on_open_keybindings()");
    dialog->set_modal(true);
    dialog->show(*this);
}

void
gui::main_window::on_open_preferences() noexcept
{
    auto dialog = Gtk::make_managed<gui::dialog::preferences>(*this, this->settings);
    dialog->signal_destroy().connect(
        [this]()
        {
            auto alert = Gtk::AlertDialog::create("Restart To Apply Settings");
            alert->set_detail("You may need to restart to apply some settings");
            alert->set_modal(true);
            alert->show(*this);
        });
}

void
gui::main_window::on_open_properties() noexcept
{
    Gtk::make_managed<gui::dialog::properties>(*this,
                                               this->file_handler_,
                                               this->view_state,
                                               this->settings);
}

void
gui::main_window::on_open_page_select() noexcept
{
    auto selector = Gtk::make_managed<gui::dialog::pageselect>(*this, this->file_handler_);
    selector->signal_selected_page().connect([this](const std::int32_t page)
                                             { this->set_page(page); });
}

void
gui::main_window::on_open_about() noexcept
{
    Gtk::make_managed<gui::dialog::about>(*this);
}

void
gui::main_window::on_open_donate() noexcept
{
    Gtk::make_managed<gui::dialog::donate>(*this);
}

/**
 * Draw the current pages and update the titlebar and statusbar.
 */
void
gui::main_window::draw_pages() noexcept
{
    if (this->waiting_for_redraw_)
    {
        // Don't stack up redraws.
        return;
    }

    this->waiting_for_redraw_ = true;

    Glib::signal_idle().connect([this]() { return this->_draw_pages(); }, Glib::PRIORITY_HIGH_IDLE);
}

bool
gui::main_window::_draw_pages() noexcept
{
    const auto image_handler = this->file_handler_->image_handler();

    this->viewport_.hide_images();

    if (!this->file_handler_->is_file_loaded())
    {
        this->thumb_sidebar_.set_visible(false);
        this->waiting_for_redraw_ = false;
        return false;
    }

    if (!this->settings->hide_thumbar)
    {
        this->thumb_sidebar_.set_visible(true);
    }

    if (!image_handler->is_page_available())
    {
        this->waiting_for_redraw_ = false;
        return false;
    }

    // Limited to at most 2 pages
    const auto pixbuf_count = this->view_state->is_displaying_double() ? 2 : 1;
    auto pixbuf_list = image_handler->get_pixbufs(pixbuf_count);
    if (this->settings->default_manga_mode && this->view_state->is_displaying_double())
    {
        std::swap(pixbuf_list[0], pixbuf_list[1]);
    }

    std::vector<std::array<std::int32_t, 2>> size_list;
    for (const auto& pixbuf : pixbuf_list)
    {
        size_list.push_back({pixbuf->get_width(), pixbuf->get_height()});
    }

    // Rotation handling
    switch (this->settings->rotation)
    {
        case 0:
        {
            this->viewport_.set_orientation(Gtk::Orientation::HORIZONTAL);
            break;
        }
        case 90:
        {
            this->viewport_.set_orientation(Gtk::Orientation::VERTICAL);
            std::ranges::for_each(size_list, [](auto& list) { std::ranges::reverse(list); });
            break;
        }
        case 180:
        {
            this->viewport_.set_orientation(Gtk::Orientation::HORIZONTAL);
            if (this->view_state->is_displaying_double())
            {
                std::swap(pixbuf_list[0], pixbuf_list[1]);
            }
            break;
        }
        case 270:
        {
            this->viewport_.set_orientation(Gtk::Orientation::VERTICAL);
            std::ranges::for_each(size_list, [](auto& list) { std::ranges::reverse(list); });
            if (this->view_state->is_displaying_double())
            {
                std::swap(pixbuf_list[0], pixbuf_list[1]);
            }
            break;
        }
        default:
            std::unreachable();
    }

    const auto [max_width, max_height] = this->get_visible_area_size();

    std::vector<std::array<std::int32_t, 2>> scaled_sizes;

    for (std::size_t i = 0; std::cmp_less(i, pixbuf_count); ++i)
    {
        auto paintable = gui::lib::image_tools::fit_to_rectangle(pixbuf_list[i],
                                                                 max_width,
                                                                 max_height,
                                                                 this->settings->rotation);

        scaled_sizes.push_back(
            {paintable->get_intrinsic_width(), paintable->get_intrinsic_height()});
        // logger::debug<logger::gui>("scaled_sizes[{}] {}x{}", i, scaled_sizes[i][0], scaled_sizes[i][1]);

        if (i == 0)
        {
            this->viewport_.set_left(paintable);
        }
        else
        {
            this->viewport_.set_right(paintable);
        }
    }

    this->statusbar_.set_resolution(scaled_sizes, size_list);
    this->statusbar_.update();

    this->waiting_for_redraw_ = false;

    return false;
}

void
gui::main_window::update_page_information() noexcept
{
    const auto image_handler = this->file_handler_->image_handler();

    const auto page = image_handler->get_current_page();
    if (page == 0)
    {
        return;
    }

    auto filenames = image_handler->get_page_filename(page);
    for (auto& filename : filenames)
    {
        filename = std::filesystem::path(filename).filename();
    }

    const auto filesizes = image_handler->get_page_filesize(page);

    const auto filename = ztd::join(filenames, ", ");
    const auto filesize = ztd::join(filesizes, ", ");

    this->statusbar_.set_page_number(page, image_handler->get_number_of_pages());
    this->statusbar_.set_filename(filename);
    this->statusbar_.set_filesize(filesize);
    this->statusbar_.update();
}

bool
gui::main_window::get_virtual_double_page(const std::optional<page_t> query) noexcept
{
    const auto page = query.value_or(this->file_handler_->image_handler()->get_current_page());

    if (page == 1 &&
        this->settings->virtual_double_page_for_fitting_images &
            config::double_page::as_one_title &&
        file_handler_->is_archive())
    {
        return true;
    }

    if (!this->settings->default_double_page ||
        !(this->settings->virtual_double_page_for_fitting_images &
          config::double_page::as_one_wide) ||
        this->file_handler_->image_handler()->is_last_page(page))
    {
        return false;
    }

    for (const auto p : {page, page + 1})
    {
        if (!this->file_handler_->image_handler()->is_page_available(p))
        {
            return false;
        }

        const auto [width, height] = this->file_handler_->image_handler()->get_page_size(p);
        if (width > height)
        {
            return true;
        }
    }
    return false;
}

void
gui::main_window::page_available(const page_t page) noexcept
{
    // Called whenever a new page is ready for displaying
    const auto image_handler = this->file_handler_->image_handler();

    this->thumb_sidebar_.request(page, image_handler->get_path_to_page(page));

    // Refresh display when currently opened page becomes available.
    const auto current_page = image_handler->get_current_page();
    const auto nb_pages = this->view_state->is_displaying_double() ? 2 : 1;

    if (current_page <= page && page < (current_page + nb_pages))
    {
        this->displayed_double();
        this->draw_pages();
        this->update_page_information();
    }
}

void
gui::main_window::on_file_opened() noexcept
{
    this->displayed_double();

    if (!this->settings->hide_thumbar)
    {
        this->thumb_sidebar_.set_visible(true);
    }

    if (this->settings->statusbar.archive_filename_fullpath)
    {
        this->statusbar_.set_archive_filename(this->file_handler_->get_base_path());
    }
    else
    {
        this->statusbar_.set_archive_filename(this->file_handler_->get_base_path().filename());
    }
    this->statusbar_.set_view_mode();
    this->statusbar_.set_filesize_archive(this->file_handler_->get_base_path());
    const auto n = this->file_handler_->get_file_number();
    this->statusbar_.set_file_number(n[0], n[1]);
    this->statusbar_.update();
}

void
gui::main_window::on_file_closed() noexcept
{
    if (GTK_IS_WINDOW(this->gobj()))
    {
        // this will get called during program shutdown
        // then 'this' is no longer a Window, so need to
        // check if the Window is still valid first.
        this->set_title(PACKAGE_NAME);
    }

    this->viewport_.hide_images();
    this->statusbar_.set_message("");
    this->thumb_sidebar_.set_visible(false);
    this->thumb_sidebar_.clear();
}

void
gui::main_window::set_page(const page_t page) noexcept
{
    const auto image_handler = this->file_handler_->image_handler();

    if (page == image_handler->get_current_page())
    {
        return;
    }

    image_handler->set_page(page);

    this->displayed_double();

    this->thumb_sidebar_.set_page(page);

    this->update_page_information();

    if (!this->settings->keep_transformation)
    {
        this->settings->rotation = 0;
    }

    this->draw_pages();
}

bool
gui::main_window::flip_page(const page_t number_of_pages, bool single_step) noexcept
{
    if (!this->file_handler_->is_file_loaded())
    {
        return false;
    }

    const auto image_handler = this->file_handler_->image_handler();

    const auto current_page = image_handler->get_current_page();
    const auto current_number_of_pages = image_handler->get_number_of_pages();

    auto new_page = current_page + number_of_pages;
    if (std::abs(number_of_pages) == 1 && !single_step && this->settings->default_double_page &&
        this->settings->double_step_in_double_page_mode)
    {
        if (number_of_pages == 1 && !this->get_virtual_double_page())
        {
            new_page += 1;
        }
        else if (number_of_pages == -1 && !this->get_virtual_double_page(new_page - 1))
        {
            new_page -= 1;
        }
    }

    if (new_page <= 0)
    {
        // Only switch to previous page when flipping one page before the
        // first one. (Note: checking for (page number <= 1) to handle empty
        // archive case).
        if (number_of_pages == -1 && current_page <= 1)
        {
            return this->file_handler_->open_prev_archive();
        }
        // Handle empty archive case.
        new_page = std::min<page_t>(1, current_number_of_pages);
    }
    else if (new_page > current_number_of_pages)
    {
        if (number_of_pages == 1)
        {
            return this->file_handler_->open_next_archive();
        }
        new_page = current_number_of_pages;
    }

    if (new_page != current_page)
    {
        this->set_page(new_page);
        return true;
    }
    return false;
}

void
gui::main_window::first_page() noexcept
{
    const auto image_handler = this->file_handler_->image_handler();
    const auto number_of_pages = image_handler->get_number_of_pages();
    if (number_of_pages)
    {
        this->set_page(1);
    }
}

void
gui::main_window::last_page() noexcept
{
    const auto image_handler = this->file_handler_->image_handler();
    const auto number_of_pages = image_handler->get_number_of_pages();
    if (number_of_pages)
    {
        this->set_page(number_of_pages);
    }
}

void
gui::main_window::rotate_x(const std::int32_t rotation) noexcept
{
    this->settings->rotation = (this->settings->rotation + rotation) % 360;

    this->draw_pages();
}

void
gui::main_window::change_double_page() noexcept
{
    this->settings->default_double_page = !this->settings->default_double_page;
    this->displayed_double();
    this->update_page_information();

    this->draw_pages();
}

void
gui::main_window::change_manga_mode() noexcept
{
    this->settings->default_manga_mode = !this->settings->default_manga_mode;

    this->view_state->set_manga_mode(this->settings->default_manga_mode);

    this->statusbar_.set_view_mode();
    this->update_page_information();

    this->draw_pages();
}

void
gui::main_window::change_fullscreen() noexcept
{
    if (this->is_fullscreen())
    {
        this->unfullscreen();

        if (this->settings->fullscreen.hide_thumbar && !this->settings->hide_thumbar)
        {
            this->thumb_sidebar_.set_visible(true);
        }
        if (this->settings->fullscreen.hide_statusbar && !this->settings->hide_statusbar)
        {
            this->statusbar_.set_visible(true);
        }
        if (this->settings->fullscreen.hide_menubar && !this->settings->hide_menubar)
        {
            this->menubar_.set_visible(true);
        }
    }
    else
    {
        this->fullscreen();

        if (this->settings->fullscreen.hide_thumbar || this->settings->hide_thumbar)
        {
            this->thumb_sidebar_.set_visible(false);
        }
        if (this->settings->fullscreen.hide_statusbar || this->settings->hide_statusbar)
        {
            this->statusbar_.set_visible(false);
        }
        if (this->settings->fullscreen.hide_menubar || this->settings->hide_menubar)
        {
            this->menubar_.set_visible(false);
        }
    }
}

void
gui::main_window::displayed_double() noexcept
{
    // sets True if two pages are currently displayed
    const auto image_handler = this->file_handler_->image_handler();

    this->view_state->set_displaying_double(
        image_handler->get_current_page() != 0 && this->settings->default_double_page &&
        !this->get_virtual_double_page() && !image_handler->is_last_page());
}

std::array<std::int32_t, 2>
gui::main_window::get_visible_area_size() noexcept
{
    const auto display = this->get_display();
    const auto surface = this->get_surface();
    const auto monitor = display->get_monitor_at_surface(surface);
    Gdk::Rectangle geometry;
    monitor->get_geometry(geometry);

    return {geometry.get_width(), geometry.get_height()};
}

void
gui::main_window::on_move_current_file() noexcept
{
    const auto current_file = this->file_handler_->current_file();

    this->on_trash_or_move_load_next_file();

    const auto target =
        current_file.parent_path() / this->settings->move_file / current_file.filename();
    if (!std::filesystem::exists(target.parent_path()))
    {
        std::filesystem::create_directories(target.parent_path());
    }

    std::error_code ec;
    std::filesystem::rename(current_file, target, ec);
    if (ec)
    {
        auto alert = Gtk::AlertDialog::create("Failed To Move File!");
        alert->set_detail(std::format("From: {}\nTo:   {}\nReason: {}",
                                      current_file.string(),
                                      target.string(),
                                      ec.message()));
        alert->set_modal(true);
        alert->show(*this);
    }
}

void
gui::main_window::on_trash_current_file() noexcept
{
    const auto current_file = this->file_handler_->current_file();

    auto dialog = Gtk::AlertDialog::create("Trash Current File?");
    dialog->set_detail(std::format("{}", current_file.string()));
    dialog->set_modal(true);
    dialog->set_buttons({"Cancel", "Confirm"});
    dialog->set_cancel_button(0);
    dialog->set_default_button(0);

    auto slot = [this, current_file, dialog](Glib::RefPtr<Gio::AsyncResult>& result)
    {
        try
        {
            const auto response = dialog->choose_finish(result);
            if (response == 1)
            { // Confirm Button
                this->on_trash_or_move_load_next_file();
                auto trash_result = vfs::trash_can::trash(current_file);
                if (!trash_result)
                {
                    auto alert = Gtk::AlertDialog::create("Failed To Trash File!");
                    alert->set_detail(std::format("File: {}", current_file.string()));
                    alert->set_modal(true);
                    alert->show(*this);
                }
            }
        }
        catch (const Gtk::DialogError& err)
        {
            logger::error<logger::gui>("Gtk::AlertDialog error: {}", err.what());
        }
        catch (const Glib::Error& err)
        {
            logger::error<logger::gui>("Unexpected exception: {}", err.what());
        }
    };
    dialog->choose(*this, slot);
}

void
gui::main_window::on_trash_or_move_load_next_file() noexcept
{
    if (this->file_handler_->is_archive())
    {
        bool next_opened = this->file_handler_->open_next_archive();
        if (!next_opened)
        {
            next_opened = this->file_handler_->open_prev_archive();
        }
        if (!next_opened)
        {
            this->file_handler_->close_file();
        }
    }
    else
    {
        const auto image_handler = this->file_handler_->image_handler();
        if (image_handler->get_number_of_pages() > 1)
        {
            if (image_handler->is_last_page())
            {
                this->flip_page(-1);
            }
            else
            {
                this->flip_page(1);
            }
        }
        else
        {
            this->file_handler_->close_file();
        }
    }
}

void
gui::main_window::on_escape_event() noexcept
{
    if (this->is_fullscreen())
    {
        this->change_fullscreen();
    }
    else
    {
        this->close();
    }
}
