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

#include "gui/dialog/about.hxx"
#include "gui/dialog/bookmarks.hxx"
#include "gui/dialog/donate.hxx"
#include "gui/dialog/preferences.hxx"
#include "gui/dialog/properties.hxx"

#include "vfs/image-tools/image-tools.hxx"
#include "vfs/trash-can.hxx"
#include "vfs/user-dirs.hxx"

#include "logger.hxx"

gui::main_window::main_window(const Glib::RefPtr<Gtk::Application>& app,
                              const std::vector<std::filesystem::path>& filelist) noexcept
{
    set_application(app);
    assert(get_application() != nullptr);

    set_title(PACKAGE_NAME_WEBCOMIX_FANCY);
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
    file_handler_->signal_page_set().connect([this](const std::int32_t page) { set_page(page); });

    file_handler_->signal_extraction_finished().connect([this]() { draw_pages(); });

    app->add_action("archive_next", [this]() { auto _ = file_handler_->open_next_archive(); });
    app->add_action("archive_prev", [this]() { auto _ = file_handler_->open_prev_archive(); });

    app->add_action("archive_first", [this]() { auto _ = file_handler_->open_first_archive(); });
    app->add_action("archive_last", [this]() { auto _ = file_handler_->open_last_archive(); });

    app->add_action("bookmark_add", [this]() { on_bookmark_add(); });
    app->add_action("bookmark_manager", [this]() { on_bookmark_manager(); });

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
    app->add_action("properties", [this]() { on_open_properties(); });
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
    if (!file_handler_->is_file_loaded())
    {
        return;
    }

    const auto image_handler = file_handler_->image_handler();

    bookmarks_->add({file_handler_->get_real_path(),
                     1,
                     image_handler->get_number_of_pages(),
                     std::chrono::system_clock::now()});
}

void
gui::main_window::on_bookmark_manager() noexcept
{
    Gtk::make_managed<gui::dialog::bookmarks>(*this, file_handler_, bookmarks_, settings);
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
    if (!file_handler_->is_file_loaded())
    {
        return;
    }

    Gtk::make_managed<gui::dialog::properties>(*this, file_handler_, settings);
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

    auto images = image_handler->get_images(image_handler->get_number_of_pages());
    for (const auto& image : images)
    {
        auto paintable =
            vfs::image_tools::fit_to_rectangle(image, image->get_width(), image->get_height(), 0);

        viewport_.add_picture(paintable);
    }

    // statusbar_.update();

    waiting_for_redraw_ = false;

    return false;
}

void
gui::main_window::update_page_information() noexcept
{
    const auto image_handler = file_handler_->image_handler();

    statusbar_.set_page_number(image_handler->get_number_of_pages());
    statusbar_.update();
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
    statusbar_.set_filesize_archive(file_handler_->get_base_path());
    const auto n = file_handler_->get_file_number();
    statusbar_.set_file_number(n[0], n[1]);
    statusbar_.update();
}

void
gui::main_window::on_file_closed() noexcept
{
    set_title(PACKAGE_NAME_WEBCOMIX_FANCY);

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

    draw_pages();
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
#if 0
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
#else
        file_handler_->close_file();
#endif
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
