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
#include <ranges>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

#include <cmath>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include <ztd/ztd.hxx>

#include "gui/main-window.hxx"
#include "gui/menubar.hxx"
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
                              const std::vector<std::filesystem::path>& filelist) noexcept
{
    set_application(app);
    assert(get_application() != nullptr);

    set_title(PACKAGE_NAME_FANCY);
    set_size_request(500, 500);
    set_resizable(true);
    set_visible(true);

    config_manager_->signal_load_error().connect(
        [this](const std::string& msg)
        {
            auto dialog = Gtk::AlertDialog::create("Config Load Error");
            dialog->set_detail(msg);
            dialog->set_modal(true);
            dialog->show(*this);
        });
    config_manager_->signal_save_error().connect(
        [this](const std::string& msg)
        {
            auto dialog = Gtk::AlertDialog::create("Config Save Error");
            dialog->set_detail(msg);
            dialog->set_modal(true);
            dialog->show(*this);
        });
    config_manager_->load();

    bookmarks_->signal_load_error().connect(
        [this](std::string msg)
        {
            auto dialog = Gtk::AlertDialog::create("Bookmark Load Error");
            dialog->set_detail(msg);
            dialog->set_modal(true);
            dialog->show(*this);
        });
    bookmarks_->signal_save_error().connect(
        [this](std::string msg)
        {
            auto dialog = Gtk::AlertDialog::create("Bookmark Save Error");
            dialog->set_detail(msg);
            dialog->set_modal(true);
            dialog->show(*this);
        });
    bookmarks_->load();

    file_handler_->signal_file_opened().connect([this]() { on_file_opened(); });
    file_handler_->signal_file_closed().connect([this]() { on_file_closed(); });
    file_handler_->signal_page_available().connect([this](const page_t page)
                                                   { page_available(page); });
    file_handler_->signal_page_set().connect([this](const page_t page) { set_page(page); });

    app->add_action("page_next", [this]() { flip_page(1); });
    app->add_action("page_prev", [this]() { flip_page(-1); });
    app->add_action("page_next_single", [this]() { flip_page(1, true); });
    app->add_action("page_prev_single", [this]() { flip_page(-1, true); });
    app->add_action("page_next_ff", [this]() { flip_page(settings->page_ff_step); });
    app->add_action("page_prev_ff", [this]() { flip_page(-settings->page_ff_step); });
    app->add_action("page_first", [this]() { first_page(); });
    app->add_action("page_last", [this]() { last_page(); });
    app->add_action("page_select", [this]() { on_open_page_select(); });

    app->add_action("archive_next", [this]() { auto _ = file_handler_->open_next_archive(); });
    app->add_action("archive_prev", [this]() { auto _ = file_handler_->open_prev_archive(); });

    app->add_action("archive_first", [this]() { auto _ = file_handler_->open_first_archive(); });
    app->add_action("archive_last", [this]() { auto _ = file_handler_->open_last_archive(); });

    app->add_action("rotate_reset",
                    [this]()
                    {
                        settings->rotation = 0;
                        rotate_x(0);
                    });
    app->add_action("rotate_90", [this]() { rotate_x(90); });
    app->add_action("rotate_180", [this]() { rotate_x(180); });
    app->add_action("rotate_270", [this]() { rotate_x(270); });

    app->add_action("bookmark_add", [this]() { on_bookmark_add(); });
    app->add_action("bookmark_manager", [this]() { on_bookmark_manager(); });

    app->add_action("view_double", [this]() { change_double_page(); });
    app->add_action("view_manga", [this]() { change_manga_mode(); });

    app->add_action("toggle_thumbar",
                    [this]()
                    {
                        settings->hide_thumbar = !settings->hide_thumbar;
                        thumb_sidebar_.set_visible(!settings->hide_thumbar);
                    });
    app->add_action("toggle_menubar",
                    [this]()
                    {
                        settings->hide_menubar = !settings->hide_menubar;
                        menubar_.set_visible(!settings->hide_menubar);
                    });
    app->add_action("toggle_statusbar",
                    [this]()
                    {
                        settings->hide_statusbar = !settings->hide_statusbar;
                        statusbar_.set_visible(!settings->hide_statusbar);
                    });
    app->add_action("page_center_space", [this]() { viewport_.toggle_page_padding(); });

    app->add_action("escape", [this]() { on_escape_event(); });
    app->add_action("fullscreen", [this]() { change_fullscreen(); });

    app->add_action("close", [this]() { file_handler_->close_file(); });
    app->add_action("trash", [this]() { on_trash_current_file(); });
    app->add_action("move", [this]() { on_move_current_file(); });
    app->add_action("page_extract", [this]() { on_open_page_extractor(); });

    app->add_action("open", [this]() { on_open_filechooser(); });
    app->add_action("exit", [this]() { on_exit(); });
    app->add_action("refresh", [this]() { file_handler_->refresh_opened(); });
    app->add_action("keybindings", [this]() { on_open_keybindings(); });
    app->add_action("preferences", [this]() { on_open_preferences(); });
    app->add_action("properties", [this]() { on_open_properties(); });
    app->add_action("donate", [this]() { on_open_donate(); });
    app->add_action("about", [this]() { on_open_about(); });

    add_shortcuts();

    view_state->set_manga_mode(settings->default_manga_mode);
    view_state->set_displaying_double(false);

    thumb_sidebar_.set_visible(false);
    thumb_sidebar_.signal_page_selected().connect([this](const auto page) { set_page(page); });

    box_.set_orientation(Gtk::Orientation::VERTICAL);
    box_.set_hexpand(true);
    box_.set_vexpand(true);

    box_.append(menubar_);

    center_box_.set_orientation(Gtk::Orientation::HORIZONTAL);
    center_box_.set_hexpand(true);
    center_box_.set_vexpand(true);
    box_.append(center_box_);

    center_box_.append(thumb_sidebar_);
    center_box_.append(viewport_);

    box_.append(statusbar_);

    set_child(box_);

    if (settings->hide_thumbar)
    {
        thumb_sidebar_.set_visible(false);
    }
    if (settings->hide_statusbar)
    {
        statusbar_.set_visible(false);
    }
    if (settings->hide_menubar)
    {
        menubar_.set_visible(false);
    }

    // DnD support
    drop_target_ =
        Gtk::DropTarget::create(GDK_TYPE_FILE_LIST, Gdk::DragAction::COPY | Gdk::DragAction::MOVE);
    drop_target_->signal_drop().connect(sigc::mem_fun(*this, &main_window::on_drag_data_received),
                                        false);
    add_controller(drop_target_);

    // Use idle signal to start filehandler otherwise the
    // window will not get displayed until after open_file_init()
    // has returned. This also causes other problems since the
    // window size will be '1x1' during the initial page draw.
    Glib::signal_idle().connect_once([this, filelist]()
                                     { file_handler_->open_file_init(filelist); });
}

void
gui::main_window::add_shortcuts() noexcept
{
    auto controller = Gtk::ShortcutController::create();

    { // Exit
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.exit");
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
                activate_action("app.page_next");
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
                if (view_state->is_manga_mode())
                {
                    activate_action("app.page_prev");
                }
                else
                {
                    activate_action("app.page_next");
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
                activate_action("app.page_prev");
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
                if (view_state->is_manga_mode())
                {
                    activate_action("app.page_next");
                }
                else
                {
                    activate_action("app.page_prev");
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
                activate_action("app.page_next_single");
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
                activate_action("app.page_prev_single");
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
                activate_action("app.page_next_ff");
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
                activate_action("app.page_prev_ff");
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
                activate_action("app.page_first");
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
                activate_action("app.page_last");
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
                activate_action("app.page_select");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_g), action));
    }

    { // Next Archive
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.archive_next");
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
                activate_action("app.archive_prev");
                return true;
            });

        controller->add_shortcut(Gtk::Shortcut::create(
            Gtk::KeyvalTrigger::create(GDK_KEY_Left, Gdk::ModifierType::CONTROL_MASK),
            action));
    }

    { // First Archive
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.archive_first");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Left,
                                                             Gdk::ModifierType::CONTROL_MASK |
                                                                 Gdk::ModifierType::SHIFT_MASK),
                                  action));
    }

    { // Last Archive
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.archive_last");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Right,
                                                             Gdk::ModifierType::CONTROL_MASK |
                                                                 Gdk::ModifierType::SHIFT_MASK),
                                  action));
    }

    // View //
    { // Keep Transformation
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.keep_transformation");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_k), action));
    }

    { // Rotate 90
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.rotate_90");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_r), action));
    }

    { // Rotate 180
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.rotate_180");
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
                activate_action("app.rotate_270");
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
                activate_action("app.view_double");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_d), action));
    }

    { // Manga Mode
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.view_manga");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_m), action));
    }

    { // Toggle Douoble Page Center Spacing
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.page_center_space");
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
                activate_action("app.escape");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Escape), action));
    }

    { // Fullscreen
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.fullscreen");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_f), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_F11), action));
    }

    // Info //

    {
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.donate");
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
                activate_action("app.about");
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
                activate_action("app.close");
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
                activate_action("app.trash");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Delete), action));
    }

    { // Extract Page
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.page_extract");
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
                activate_action("app.move");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_grave), action));
    }

    { // Open
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.open");
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
                activate_action("app.preferences");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_F12), action));
    }

    { // Properties
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.properties");
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
                activate_action("app.refresh");
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
                activate_action("app.bookmark_add");
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
                activate_action("app.bookmark_manager");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_O,
                                                             Gdk::ModifierType::CONTROL_MASK |
                                                                 Gdk::ModifierType::SHIFT_MASK),
                                  action));
    }

    add_controller(controller);
}

void
gui::main_window::on_exit() noexcept
{
    config_manager_->save();

    close();
}

void
gui::main_window::on_bookmark_add() noexcept
{
    const auto image_handler = file_handler_->image_handler();

    bookmarks_->add({file_handler_->get_real_path(),
                     image_handler->get_current_page(),
                     image_handler->get_number_of_pages(),
                     std::chrono::system_clock::now()});
}

void
gui::main_window::on_bookmark_manager() noexcept
{
    Gtk::make_managed<gui::dialog::bookmarks>(*this, file_handler_, bookmarks_, settings);
}

void
gui::main_window::on_open_page_extractor() noexcept
{
    const auto path = file_handler_->image_handler()->get_path_to_page();

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

    const auto open_path = std::invoke(
        [this]()
        {
            std::filesystem::path path;
            if (file_handler_->is_file_loaded())
            {
                if (file_handler_->is_archive())
                {
                    return file_handler_->get_base_path().parent_path();
                }
                else
                {
                    return file_handler_->get_base_path();
                }
            }
            else
            {
                return vfs::user::home();
            }
        });

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
            file_handler_->open_file_init(paths);
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
    dialog->set_detail(
        "Keybinding are currently static and cannot be changed. Writing a keybinding editor is not "
        "fun. All keybindings are visible in the menu bar.");
    dialog->set_modal(true);
    dialog->show(*this);
}

void
gui::main_window::on_open_preferences() noexcept
{
    auto dialog = Gtk::make_managed<gui::dialog::preferences>(*this, settings);
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
    Gtk::make_managed<gui::dialog::properties>(*this, file_handler_, view_state, settings);
}

void
gui::main_window::on_open_page_select() noexcept
{
    auto selector = Gtk::make_managed<gui::dialog::pageselect>(*this, file_handler_);
    selector->signal_selected_page().connect([this](const std::int32_t page) { set_page(page); });
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
    if (waiting_for_redraw_)
    {
        // Don't stack up redraws.
        return;
    }

    waiting_for_redraw_ = true;

    Glib::signal_idle().connect([this]() { return _draw_pages(); }, Glib::PRIORITY_HIGH_IDLE);
}

bool
gui::main_window::_draw_pages() noexcept
{
    const auto image_handler = file_handler_->image_handler();

    viewport_.hide_images();

    if (!file_handler_->is_file_loaded())
    {
        thumb_sidebar_.set_visible(false);
        waiting_for_redraw_ = false;
        return false;
    }

    if (!settings->hide_thumbar)
    {
        thumb_sidebar_.set_visible(true);
    }

    if (!image_handler->is_page_available())
    {
        waiting_for_redraw_ = false;
        return false;
    }

    // Limited to at most 2 pages
    const auto pixbuf_count = view_state->is_displaying_double() ? 2 : 1;
    auto pixbuf_list = image_handler->get_images(pixbuf_count);
    if (settings->default_manga_mode && view_state->is_displaying_double())
    {
        std::swap(pixbuf_list[0], pixbuf_list[1]);
    }

    std::vector<std::array<std::int32_t, 2>> size_list;
    for (const auto& pixbuf : pixbuf_list)
    {
        size_list.push_back({static_cast<std::int32_t>(pixbuf->get_width()),
                             static_cast<std::int32_t>(pixbuf->get_height())});
    }

    // Rotation handling
    switch (settings->rotation)
    {
        case 0:
        {
            viewport_.set_orientation(Gtk::Orientation::HORIZONTAL);
            break;
        }
        case 90:
        {
            viewport_.set_orientation(Gtk::Orientation::VERTICAL);
            std::ranges::for_each(size_list, [](auto& list) { std::ranges::reverse(list); });
            break;
        }
        case 180:
        {
            viewport_.set_orientation(Gtk::Orientation::HORIZONTAL);
            if (view_state->is_displaying_double())
            {
                std::swap(pixbuf_list[0], pixbuf_list[1]);
            }
            break;
        }
        case 270:
        {
            viewport_.set_orientation(Gtk::Orientation::VERTICAL);
            std::ranges::for_each(size_list, [](auto& list) { std::ranges::reverse(list); });
            if (view_state->is_displaying_double())
            {
                std::swap(pixbuf_list[0], pixbuf_list[1]);
            }
            break;
        }
        default:
            std::unreachable();
    }

    const auto [max_width, max_height] = get_visible_area_size();

    std::vector<std::array<std::int32_t, 2>> scaled_sizes;
    std::vector<Glib::RefPtr<Gdk::Paintable>> paintables;
    for (const auto& [idx, pixbuf] : std::views::enumerate(pixbuf_list))
    {
        auto paintable = gui::lib::image_tools::fit_to_rectangle(pixbuf,
                                                                 max_width,
                                                                 max_height,
                                                                 settings->rotation);

        scaled_sizes.push_back(
            {paintable->get_intrinsic_width(), paintable->get_intrinsic_height()});
        // logger::debug<logger::gui>("scaled_sizes[{}] {}x{}", idx, scaled_sizes[idx][0], scaled_sizes[idx][1]);

        paintables.push_back(paintable);
    }
    viewport_.set(paintables);

    statusbar_.set_resolution(scaled_sizes, size_list);
    statusbar_.update();

    waiting_for_redraw_ = false;

    return false;
}

void
gui::main_window::update_page_information() noexcept
{
    const auto image_handler = file_handler_->image_handler();

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

    statusbar_.set_page_number(page, image_handler->get_number_of_pages());
    statusbar_.set_filename(filename);
    statusbar_.set_filesize(filesize);
    statusbar_.update();
}

bool
gui::main_window::get_virtual_double_page(const std::optional<page_t> query) noexcept
{
    const auto page = query.value_or(file_handler_->image_handler()->get_current_page());

    if (page == 1 &&
        settings->virtual_double_page_for_fitting_images & config::double_page::as_one_title &&
        file_handler_->is_archive())
    {
        return true;
    }

    if (!settings->default_double_page ||
        !(settings->virtual_double_page_for_fitting_images & config::double_page::as_one_wide) ||
        file_handler_->image_handler()->is_last_page(page))
    {
        return false;
    }

    for (const auto p : {page, page + 1})
    {
        if (!file_handler_->image_handler()->is_page_available(p))
        {
            return false;
        }

        const auto [width, height] = file_handler_->image_handler()->get_page_size(p);
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
    const auto image_handler = file_handler_->image_handler();

    thumb_sidebar_.request(page, image_handler->get_path_to_page(page));

    // Refresh display when currently opened page becomes available.
    const auto current_page = image_handler->get_current_page();
    const auto nb_pages = view_state->is_displaying_double() ? 2 : 1;

    if (current_page <= page && page < (current_page + nb_pages))
    {
        displayed_double();
        draw_pages();
        update_page_information();
    }
}

void
gui::main_window::on_file_opened() noexcept
{
    displayed_double();

    if (!settings->hide_thumbar)
    {
        thumb_sidebar_.set_visible(true);
    }

    if (settings->statusbar.archive_filename_fullpath)
    {
        statusbar_.set_archive_filename(file_handler_->get_base_path());
    }
    else
    {
        statusbar_.set_archive_filename(file_handler_->get_base_path().filename());
    }
    statusbar_.set_view_mode();
    statusbar_.set_filesize_archive(file_handler_->get_base_path());
    const auto n = file_handler_->get_file_number();
    statusbar_.set_file_number(n[0], n[1]);
    statusbar_.update();
}

void
gui::main_window::on_file_closed() noexcept
{
    set_title(PACKAGE_NAME_FANCY);

    viewport_.hide_images();
    statusbar_.set_message("");
    thumb_sidebar_.set_visible(false);
    thumb_sidebar_.clear();
}

void
gui::main_window::set_page(const page_t page) noexcept
{
    const auto image_handler = file_handler_->image_handler();

    if (page == image_handler->get_current_page())
    {
        return;
    }

    image_handler->set_page(page);

    displayed_double();

    thumb_sidebar_.set_page(page);

    update_page_information();

    if (!settings->keep_transformation)
    {
        settings->rotation = 0;
    }

    draw_pages();
}

void
gui::main_window::flip_page(const page_t number_of_pages, bool single_step) noexcept
{
    if (!file_handler_->is_file_loaded())
    {
        return;
    }

    const auto image_handler = file_handler_->image_handler();

    const auto current_page = image_handler->get_current_page();
    const auto current_number_of_pages = image_handler->get_number_of_pages();

    auto new_page = current_page + number_of_pages;
    if (std::abs(number_of_pages) == 1 && !single_step && settings->default_double_page &&
        settings->double_step_in_double_page_mode)
    {
        if (number_of_pages == 1 && !get_virtual_double_page())
        {
            new_page += 1;
        }
        else if (number_of_pages == -1 && !get_virtual_double_page(new_page - 1))
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
            if (settings->confirm_archive_change)
            {
                auto dialog = Gtk::AlertDialog::create("Open Previous Archive?");
                dialog->set_modal(true);
                dialog->set_buttons({"Cancel", "Confirm"});
                dialog->set_cancel_button(0);
                dialog->set_default_button(1);

                auto slot = [this, dialog](Glib::RefPtr<Gio::AsyncResult>& result)
                {
                    try
                    {
                        const auto response = dialog->choose_finish(result);
                        if (response == 1)
                        { // Confirm Button
                            auto _ = file_handler_->open_prev_archive();
                        }
                    }
                    catch (...)
                    {
                        //
                    }
                };
                dialog->choose(*this, slot);
            }
            else
            {
                auto _ = file_handler_->open_prev_archive();
            }
            return;
        }
        // Handle empty archive case.
        new_page = std::min<page_t>(1, current_number_of_pages);
    }
    else if (new_page > current_number_of_pages)
    {
        if (number_of_pages == 1)
        {
            if (settings->confirm_archive_change)
            {
                auto dialog = Gtk::AlertDialog::create("Open Next Archive?");
                dialog->set_modal(true);
                dialog->set_buttons({"Cancel", "Confirm"});
                dialog->set_cancel_button(0);
                dialog->set_default_button(1);

                auto slot = [this, dialog](Glib::RefPtr<Gio::AsyncResult>& result)
                {
                    try
                    {
                        const auto response = dialog->choose_finish(result);
                        if (response == 1)
                        { // Confirm Button
                            auto _ = file_handler_->open_next_archive();
                        }
                    }
                    catch (...)
                    {
                        //
                    }
                };
                dialog->choose(*this, slot);
            }
            else
            {
                auto _ = file_handler_->open_next_archive();
            }
            return;
        }
        new_page = current_number_of_pages;
    }

    if (new_page != current_page)
    {
        set_page(new_page);
    }
}

void
gui::main_window::first_page() noexcept
{
    const auto image_handler = file_handler_->image_handler();
    const auto number_of_pages = image_handler->get_number_of_pages();
    if (number_of_pages)
    {
        set_page(1);
    }
}

void
gui::main_window::last_page() noexcept
{
    const auto image_handler = file_handler_->image_handler();
    const auto number_of_pages = image_handler->get_number_of_pages();
    if (number_of_pages)
    {
        set_page(number_of_pages);
    }
}

void
gui::main_window::rotate_x(const std::int32_t rotation) noexcept
{
    settings->rotation = (settings->rotation + rotation) % 360;

    draw_pages();
}

void
gui::main_window::change_double_page() noexcept
{
    settings->default_double_page = !settings->default_double_page;
    displayed_double();
    update_page_information();

    draw_pages();
}

void
gui::main_window::change_manga_mode() noexcept
{
    settings->default_manga_mode = !settings->default_manga_mode;

    view_state->set_manga_mode(settings->default_manga_mode);

    statusbar_.set_view_mode();
    update_page_information();

    draw_pages();
}

void
gui::main_window::change_fullscreen() noexcept
{
    if (is_fullscreen())
    {
        unfullscreen();

        if (settings->fullscreen.hide_thumbar && !settings->hide_thumbar)
        {
            thumb_sidebar_.set_visible(true);
        }
        if (settings->fullscreen.hide_statusbar && !settings->hide_statusbar)
        {
            statusbar_.set_visible(true);
        }
        if (settings->fullscreen.hide_menubar && !settings->hide_menubar)
        {
            menubar_.set_visible(true);
        }
    }
    else
    {
        fullscreen();

        if (settings->fullscreen.hide_thumbar || settings->hide_thumbar)
        {
            thumb_sidebar_.set_visible(false);
        }
        if (settings->fullscreen.hide_statusbar || settings->hide_statusbar)
        {
            statusbar_.set_visible(false);
        }
        if (settings->fullscreen.hide_menubar || settings->hide_menubar)
        {
            menubar_.set_visible(false);
        }
    }
}

void
gui::main_window::displayed_double() noexcept
{
    // sets True if two pages are currently displayed
    const auto image_handler = file_handler_->image_handler();

    view_state->set_displaying_double(image_handler->get_current_page() != 0 &&
                                      settings->default_double_page && !get_virtual_double_page() &&
                                      !image_handler->is_last_page());
}

std::array<std::int32_t, 2>
gui::main_window::get_visible_area_size() noexcept
{
    const auto display = get_display();
    const auto surface = get_surface();
    const auto monitor = display->get_monitor_at_surface(surface);
    Gdk::Rectangle geometry;
    monitor->get_geometry(geometry);

    return {geometry.get_width(), geometry.get_height()};
}

void
gui::main_window::on_move_current_file() noexcept
{
    const auto current_file = file_handler_->current_file();

    on_trash_or_move_load_next_file();

    const auto target = current_file.parent_path() / settings->move_file / current_file.filename();
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
    const auto current_file = file_handler_->current_file();

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
                on_trash_or_move_load_next_file();
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
    if (file_handler_->is_archive())
    {
        bool next_opened = file_handler_->open_next_archive();
        if (!next_opened)
        {
            next_opened = file_handler_->open_prev_archive();
        }
        if (!next_opened)
        {
            file_handler_->close_file();
        }
    }
    else
    {
        const auto image_handler = file_handler_->image_handler();
        if (image_handler->get_number_of_pages() > 1)
        {
            if (image_handler->is_last_page())
            {
                flip_page(-1);
            }
            else
            {
                flip_page(1);
            }
        }
        else
        {
            file_handler_->close_file();
        }
    }
}

bool
gui::main_window::on_drag_data_received(const Glib::ValueBase& value, double x, double y) noexcept
{
    (void)x;
    (void)y;

    Glib::Value<GSList*> gslist_value;
    gslist_value.init(value.gobj());
    auto files = Glib::SListHandler<Glib::RefPtr<Gio::File>>::slist_to_vector(
        gslist_value.get(),
        Glib::OwnershipType::OWNERSHIP_NONE);

    std::vector<std::filesystem::path> paths;
    for (const auto& file : files)
    {
        // logger::debug<logger::gui>("DnD Source: {}", file->get_path());
        paths.push_back(file->get_path());
    }

    Glib::signal_idle().connect_once([this, paths]() { file_handler_->open_file_init(paths); });

    return true;
}

void
gui::main_window::on_escape_event() noexcept
{
    if (is_fullscreen())
    {
        change_fullscreen();
    }
    else
    {
        close();
    }
}
