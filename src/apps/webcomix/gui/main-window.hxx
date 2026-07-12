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

#pragma once

#include <array>
#include <filesystem>
#include <memory>
#include <optional>
#include <vector>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include "settings/config.hxx"
#include "settings/settings.hxx"

#include "gui/menubar.hxx"
#include "gui/statusbar.hxx"
#include "gui/viewport.hxx"

#include "vfs/bookmarks.hxx"
#include "vfs/file-handler.hxx"

namespace gui
{
class main_window : public Gtk::ApplicationWindow
{
  public:
    explicit main_window(const Glib::RefPtr<Gtk::Application>& app,
                         const std::vector<std::filesystem::path>& filelist) noexcept;

  private:
    void draw_pages() noexcept;
    bool _draw_pages() noexcept;
    void set_page(const std::int32_t page) noexcept;
    void first_page() noexcept;
    void last_page() noexcept;
    void change_fullscreen() noexcept;

    void update_page_information() noexcept;

    void on_file_opened() noexcept;
    void on_file_closed() noexcept;

    void add_shortcuts() noexcept;

    void on_bookmark_add() noexcept;
    void on_bookmark_manager() noexcept;

    void on_exit() noexcept;
    void on_escape_event() noexcept;
    void on_open_filechooser() noexcept;
    void on_open_keybindings() noexcept;
    void on_open_preferences() noexcept;
    void on_open_properties() noexcept;
    void on_open_page_select() noexcept;
    void on_open_about() noexcept;
    void on_open_donate() noexcept;

    void on_move_current_file() noexcept;
    void on_trash_current_file() noexcept;
    void on_trash_or_move_load_next_file() noexcept; // shared logic

    std::shared_ptr<config::settings> settings = std::make_shared<config::settings>();
    std::shared_ptr<config::manager> config_manager_ = std::make_shared<config::manager>(settings);
    std::shared_ptr<vfs::file_handler> file_handler_ = std::make_shared<vfs::file_handler>();

    std::shared_ptr<vfs::bookmarks> bookmarks_ =
        std::make_shared<vfs::bookmarks>(vfs::bookmarks::frontend::webcomix);

    bool waiting_for_redraw_{false};

    std::array<std::filesystem::path, 2> current_images_;

    Gtk::Box box_;
    Gtk::Box center_box_;

    gui::menubar menubar_ = gui::menubar();
    gui::viewport viewport_ = gui::viewport(settings);
    gui::statusbar statusbar_ = gui::statusbar(settings);

    bool on_drag_data_received(const Glib::ValueBase& value, double x, double y) noexcept;
    Glib::RefPtr<Gtk::DropTarget> drop_target_;
};
} // namespace gui
