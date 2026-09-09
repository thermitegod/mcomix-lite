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
#include <span>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

#include <cassert>
#include <cmath>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include <ztd/ztd.hxx>

#include "gui/main-window.hxx"
#include "gui/menubar.hxx"
#include "gui/statusbar.hxx"

#include "gui/dialog/about.hxx"
#include "gui/dialog/donate.hxx"
#include "gui/dialog/preferences.hxx"

#include "vfs/image-tools/image-tools.hxx"
#include "vfs/trash-can.hxx"
#include "vfs/user-dirs.hxx"

#include "logger.hxx"

gui::main_window::main_window(const Glib::RefPtr<Gtk::Application>& app,
                              std::span<const std::filesystem::path> filelist) noexcept
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

    file_handler_->signal_file_opened().connect([this]() { on_file_opened(); });
    file_handler_->signal_file_closed().connect([this]() { on_file_closed(); });
    file_handler_->signal_page_available().connect([this](const std::int32_t page)
                                                   { page_available(page); });
    file_handler_->signal_page_set().connect([this](const std::int32_t page) { set_page(page); });

    app->add_action("page_next", [this]() { flip_page(1); });
    app->add_action("page_prev", [this]() { flip_page(-1); });
    app->add_action("page_first", [this]() { first_page(); });
    app->add_action("page_last", [this]() { last_page(); });

    app->add_action("rotate_reset",
                    [this]()
                    {
                        settings->rotation = 0;
                        rotate_x(0);
                    });
    app->add_action("rotate_90", [this]() { rotate_x(90); });
    app->add_action("rotate_180", [this]() { rotate_x(180); });
    app->add_action("rotate_270", [this]() { rotate_x(270); });

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

    app->add_action("escape", [this]() { on_escape_event(); });
    app->add_action("fullscreen", [this]() { change_fullscreen(); });

    app->add_action("close", [this]() { file_handler_->close_file(); });
    app->add_action("trash", [this]() { on_trash_current_file(); });
    app->add_action("move", [this]() { on_move_current_file(); });

    app->add_action("open", [this]() { on_open_filechooser(); });
    app->add_action("exit", [this]() { on_exit(); });
    app->add_action("refresh", [this]() { file_handler_->refresh_opened(); });
    app->add_action("keybindings", [this]() { on_open_keybindings(); });
    app->add_action("preferences", [this]() { on_open_preferences(); });
    app->add_action("donate", [this]() { on_open_donate(); });
    app->add_action("about", [this]() { on_open_about(); });

    add_shortcuts();

    box_.set_orientation(Gtk::Orientation::VERTICAL);
    box_.set_hexpand(true);
    box_.set_vexpand(true);

    box_.append(menubar_);

    center_box_.set_orientation(Gtk::Orientation::HORIZONTAL);
    center_box_.set_hexpand(true);
    center_box_.set_vexpand(true);
    box_.append(center_box_);

    center_box_.append(viewport_);

    box_.append(statusbar_);

    set_child(box_);

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
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Right), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Right), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Down), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Down), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Page_Down), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Page_Down), action));
    }

    { // Previous Page
        auto action = Gtk::CallbackAction::create(
            [this](Gtk::Widget&, const Glib::VariantBase&)
            {
                activate_action("app.page_prev");
                return true;
            });

        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Left), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Left), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Up), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Up), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_Page_Up), action));
        controller->add_shortcut(
            Gtk::Shortcut::create(Gtk::KeyvalTrigger::create(GDK_KEY_KP_Page_Up), action));
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

    add_controller(controller);
}

void
gui::main_window::on_exit() noexcept
{
    config_manager_->save();

    close();
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
    Gtk::make_managed<gui::dialog::preferences>(*this, settings);
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
        waiting_for_redraw_ = false;
        return false;
    }

    if (!image_handler->is_page_available())
    {
        waiting_for_redraw_ = false;
        return false;
    }

    auto images = image_handler->get_images(1);
    if (images.empty())
    {
        waiting_for_redraw_ = false;
        return false;
    }
    auto image = images[0];

    std::array<std::int32_t, 2> size_list = {static_cast<std::int32_t>(image->get_width()),
                                             static_cast<std::int32_t>(image->get_height())};

    const auto [max_width, max_height] = get_visible_area_size();

    Glib::RefPtr<Gdk::Paintable> paintable =
        vfs::image_tools::fit_to_rectangle(image, max_width, max_height, settings->rotation);

    std::array<std::int32_t, 2> scaled_size = {paintable->get_intrinsic_width(),
                                               paintable->get_intrinsic_height()};
    // logger::debug<logger::gui>("scaled_size {}x{}", scaled_size[0], scaled_size[1]);

    viewport_.set(paintable);

    statusbar_.set_resolution(scaled_size, size_list);
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

void
gui::main_window::page_available(const std::int32_t page) noexcept
{
    // Called whenever a new page is ready for displaying
    const auto image_handler = file_handler_->image_handler();

    // Refresh display when currently opened page becomes available.
    const auto current_page = image_handler->get_current_page();
    const auto nb_pages = 1;

    if (current_page <= page && page < (current_page + nb_pages))
    {
        draw_pages();
        update_page_information();
    }
}

void
gui::main_window::on_file_opened() noexcept
{
    if (settings->statusbar.archive_filename_fullpath)
    {
        statusbar_.set_archive_filename(file_handler_->get_base_path());
    }
    else
    {
        statusbar_.set_archive_filename(file_handler_->get_base_path().filename());
    }
    statusbar_.update();
}

void
gui::main_window::on_file_closed() noexcept
{
    set_title(PACKAGE_NAME_FANCY);

    viewport_.hide_images();
    statusbar_.set_message("");
}

void
gui::main_window::set_page(const std::int32_t page) noexcept
{
    const auto image_handler = file_handler_->image_handler();

    if (page == image_handler->get_current_page())
    {
        return;
    }

    image_handler->set_page(page);

    update_page_information();

    if (!settings->keep_transformation)
    {
        settings->rotation = 0;
    }

    draw_pages();
}

void
gui::main_window::flip_page(const std::int32_t number_of_pages) noexcept
{
    if (!file_handler_->is_file_loaded())
    {
        return;
    }

    const auto image_handler = file_handler_->image_handler();

    const auto current_page = image_handler->get_current_page();
    const auto current_number_of_pages = image_handler->get_number_of_pages();

    auto new_page = current_page + number_of_pages;
    if (new_page <= 0)
    {
        first_page();
    }
    else if (new_page > current_number_of_pages)
    {
        last_page();
    }
    else if (new_page != current_page)
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
gui::main_window::change_fullscreen() noexcept
{
    if (is_fullscreen())
    {
        unfullscreen();

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
        alert->set_detail(
            std::format("From: {}\nTo:   {}\nReason: {}", current_file, target, ec.message()));
        alert->set_modal(true);
        alert->show(*this);
    }
}

void
gui::main_window::on_trash_current_file() noexcept
{
    const auto current_file = file_handler_->current_file();

    auto dialog = Gtk::AlertDialog::create("Trash Current File?");
    dialog->set_detail(std::format("{}", current_file));
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
                    alert->set_detail(std::format("File: {}", current_file));
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
