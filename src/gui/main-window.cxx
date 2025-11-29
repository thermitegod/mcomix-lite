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

#include <filesystem>
#include <format>
#include <optional>
#include <string>
#include <system_error>

#include <cmath>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include <magic_enum/magic_enum.hpp>

#include <ztd/ztd.hxx>

#include "settings/config.hxx"

#include "gui/main-window.hxx"
#include "gui/statusbar.hxx"
#include "gui/thumbbar.hxx"

#include "gui/dialog/about.hxx"
#include "gui/dialog/donate.hxx"
#include "gui/dialog/pageselect.hxx"

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

    this->file_handler_->signal_file_opened().connect([this]() { this->on_file_opened(); });
    this->file_handler_->signal_file_closed().connect([this]() { this->on_file_closed(); });
    this->file_handler_->signal_page_available().connect([this](const page_t page)
                                                         { this->page_available(page); });
    this->file_handler_->signal_page_set().connect([this](const page_t page)
                                                   { this->set_page(page); });

    this->signal_draw_page().connect([this]() { this->draw_pages(); });

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

    app->add_action("rotate_90", [this]() { this->rotate_x(90); });
    app->add_action("rotate_180", [this]() { this->rotate_x(180); });
    app->add_action("rotate_270", [this]() { this->rotate_x(270); });

    app->add_action("bookmark_add", [this]() { this->on_bookmark_add(); });
    app->add_action("bookmark_manager", [this]() { this->on_bookmark_manager(); });

    app->add_action("view_double", [this]() { this->change_double_page(); });
    app->add_action("view_manga", [this]() { this->change_manga_mode(); });

    app->add_action("page_center_space", [this]() { this->toggle_page_padding(); });

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

    this->grid_.attach(this->menubar_, 0, 0, 2, 1);
    this->grid_.attach(this->thumb_sidebar_, 0, 1, 1, 1);
    this->grid_.attach_next_to(this->box_, this->thumb_sidebar_, Gtk::PositionType::RIGHT, 1, 1);
    this->grid_.attach(this->statusbar_, 0, 2, 2, 1);
    this->set_child(this->grid_);

    this->box_.append(this->image_box_);
    this->box_.set_halign(Gtk::Align::CENTER);
    this->box_.set_valign(Gtk::Align::CENTER);
    this->box_.set_hexpand(true);
    this->box_.set_vexpand(true);

    this->image_box_.set_halign(Gtk::Align::CENTER);
    this->image_box_.set_valign(Gtk::Align::CENTER);
    this->image_box_.set_hexpand(false);
    this->image_box_.set_vexpand(false);

    this->image_left_.set_content_fit(Gtk::ContentFit::CONTAIN);
    this->image_left_.set_hexpand(true);
    this->image_left_.set_vexpand(true);
    this->image_left_.set_halign(Gtk::Align::CENTER);
    this->image_left_.set_valign(Gtk::Align::CENTER);

    if (this->settings->double_page_center_space)
    {
        this->image_left_.set_margin_end(1);
        this->image_right_.set_margin_start(1);
    }

    this->image_right_.set_content_fit(Gtk::ContentFit::CONTAIN);
    this->image_right_.set_hexpand(true);
    this->image_right_.set_vexpand(true);
    this->image_right_.set_halign(Gtk::Align::CENTER);
    this->image_right_.set_valign(Gtk::Align::CENTER);

    this->image_box_.append(this->image_left_);
    this->image_box_.append(this->image_right_);

    this->set_visible(true);

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
        section_2->append("Save AS", "app.page_extract");
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
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Page_Down), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Page_Down), action));
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
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Page_Up), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Page_Up), action));
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
    auto dialog = Gtk::AlertDialog::create("Not Implemented");
    dialog->set_detail("gui::main_window::on_bookmark_add()");
    dialog->set_modal(true);
    dialog->show(*this);
}

void
gui::main_window::on_bookmark_manager() noexcept
{
    auto dialog = Gtk::AlertDialog::create("Not Implemented");
    dialog->set_detail("gui::main_window::on_bookmark_manager()");
    dialog->set_modal(true);
    dialog->show(*this);
}

void
gui::main_window::on_open_page_extractor() noexcept
{
    auto dialog = Gtk::AlertDialog::create("Not Implemented");
    dialog->set_detail("gui::main_window::on_open_page_extractor()");
    dialog->set_modal(true);
    dialog->show(*this);
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
    auto dialog = Gtk::AlertDialog::create("Not Implemented");
    dialog->set_detail("gui::main_window::on_open_preferences()");
    dialog->set_modal(true);
    dialog->show(*this);
}

void
gui::main_window::on_open_properties() noexcept
{
    auto dialog = Gtk::AlertDialog::create("Not Implemented");
    dialog->set_detail("gui::main_window::on_open_properties()");
    dialog->set_modal(true);
    dialog->show(*this);
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

void
gui::main_window::toggle_page_padding() noexcept
{
    this->settings->double_page_center_space = !this->settings->double_page_center_space;
    if (this->image_left_.get_margin_end() == 1)
    {
        this->image_left_.set_margin_end(0);
        this->image_right_.set_margin_start(0);
    }
    else
    {
        this->image_left_.set_margin_end(1);
        this->image_right_.set_margin_start(1);
    }
}

void
gui::main_window::hide_images() noexcept
{
    // hides old images before showing new ones
    // also if in double page mode and only a single
    // image is going to be shown, prevents a ghost second image
    this->image_left_.set_visible(false);
    this->image_right_.set_visible(false);
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

    this->hide_images();

    if (!this->file_handler_->is_file_loaded())
    {
        this->thumb_sidebar_.set_visible(false);
        this->waiting_for_redraw_ = false;
        return false;
    }

    this->thumb_sidebar_.set_visible(true);

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

    std::vector<bool> do_not_transform;
    for (auto& pixbuf : pixbuf_list)
    {
        do_not_transform.push_back(gui::lib::image_tools::disable_transform(pixbuf));
    }

    std::vector<std::array<std::int32_t, 2>> size_list;
    for (const auto& pixbuf : pixbuf_list)
    {
        size_list.push_back({pixbuf->get_width(), pixbuf->get_height()});
    }

    // Rotation handling
    // apply manual rotation on whole page
    std::vector<std::int32_t> rotation_list(static_cast<std::size_t>(pixbuf_count), 0);
    const auto rotation = this->settings->rotation % 360;
    switch (rotation)
    {
        case 90:
        case 270:
            for (std::size_t i = 0; std::cmp_less(i, pixbuf_count); ++i)
            {
                std::ranges::reverse(size_list[i]);
            }
            break;
        case 180:
            break;
        default:
            break;
    }

    auto scale_to_size = [this](std::int32_t width,
                                std::int32_t height) -> std::array<std::int32_t, 2>
    {
        // const auto max_width = static_cast<std::float_t>(this->image_box_.get_width());
        // const auto max_height = static_cast<std::float_t>(this->image_box_.get_height());

        const auto [max_width, max_height] = this->get_visible_area_size();

        const auto scale_width =
            static_cast<std::float_t>(max_width) / static_cast<std::float_t>(width);
        const auto scale_height =
            static_cast<std::float_t>(max_height) / static_cast<std::float_t>(height);
        const auto scale = std::min(scale_width, scale_height);

        return {static_cast<std::int32_t>(width * scale),
                static_cast<std::int32_t>(height * scale)};
    };

    std::vector<std::array<std::int32_t, 2>> scaled_sizes;

    for (std::size_t i = 0; std::cmp_less(i, pixbuf_count); ++i)
    {
        scaled_sizes.push_back(scale_to_size(size_list[i][0], size_list[i][1]));

        rotation_list[i] = rotation;

        // logger::debug<logger::gui>("scaled_sizes[{}] {}x{}", i, scaled_sizes[i][0], scaled_sizes[i][1]);

        pixbuf_list[i] = gui::lib::image_tools::fit_pixbuf_to_rectangle(pixbuf_list[i],
                                                                        scaled_sizes[i][0],
                                                                        scaled_sizes[i][1],
                                                                        rotation_list[i]);

        if (i == 0)
        {
            this->image_left_.set_pixbuf(pixbuf_list[i]);
            this->image_left_.set_visible(true);
        }
        else
        {
            this->image_right_.set_pixbuf(pixbuf_list[i]);
            this->image_right_.set_visible(true);
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

    this->thumb_sidebar_.request(page, image_handler->image_files()->path_from_page(page));

    // Refresh display when currently opened page becomes available.
    const auto current_page = image_handler->get_current_page();
    const auto nb_pages = this->view_state->is_displaying_double() ? 2 : 1;

    if (current_page <= page && page < (current_page + nb_pages))
    {
        this->displayed_double();
        this->signal_draw_page().emit();
        this->update_page_information();
    }
}

void
gui::main_window::on_file_opened() noexcept
{
    this->displayed_double();
    this->thumb_sidebar_.set_visible(true);

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

    this->hide_images();
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

    this->thumb_sidebar_.select_page(page);

    this->update_page_information();

    if (!this->settings->keep_transformation)
    {
        this->settings->rotation = 0;
    }

    this->signal_draw_page().emit();
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

    this->signal_draw_page().emit();
}

void
gui::main_window::change_double_page() noexcept
{
    this->settings->default_double_page = !this->settings->default_double_page;
    this->displayed_double();
    this->update_page_information();

    this->signal_draw_page().emit();
}

void
gui::main_window::change_manga_mode() noexcept
{
    this->settings->default_manga_mode = !this->settings->default_manga_mode;

    this->view_state->set_manga_mode(this->settings->default_manga_mode);

    this->statusbar_.set_view_mode();
    this->update_page_information();

    this->signal_draw_page().emit();
}

void
gui::main_window::change_fullscreen() noexcept
{
    if (this->is_fullscreen())
    {
        this->unfullscreen();

        // menu/status can only be hidden in fullscreen
        this->statusbar_.set_visible(true);
        this->menubar_.set_visible(true);
    }
    else
    {
        this->fullscreen();

        if (this->settings->fullscreen_hide_statusbar)
        {
            this->statusbar_.set_visible(false);
        }
        if (this->settings->fullscreen_hide_menubar)
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

    auto slot = [this, current_file, dialog](Glib::RefPtr<Gio::AsyncResult>& result) mutable
    {
        try
        {
            switch (const auto response = dialog->choose_finish(result))
            {
                case 0: // Cancel
                    break;
                case 1: // Confirm
                    this->on_trash_or_move_load_next_file();
                    // TODO - handle error case
                    (void)vfs::trash_can::trash(current_file);
                    break;
                default:
                    logger::warn<logger::gui>("Unexpected response: {}", response);
                    break;
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
