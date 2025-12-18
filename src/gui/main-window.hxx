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

#include "settings/settings.hxx"

#include "gui/menubar.hxx"
#include "gui/statusbar.hxx"
#include "gui/thumbbar.hxx"
#include "gui/viewport.hxx"

#include "gui/lib/view-state.hxx"

#include "vfs/bookmarks.hxx"
#include "vfs/file-handler.hxx"

#include "types.hxx"

namespace gui
{
class main_window : public Gtk::ApplicationWindow
{
  public:
    main_window(const Glib::RefPtr<Gtk::Application>& app,
                const std::vector<std::filesystem::path>& filelist);

  private:
    void draw_pages() noexcept;
    bool _draw_pages() noexcept;
    void set_page(const page_t page) noexcept;
    bool flip_page(const page_t number_of_pages, bool single_step = false) noexcept;
    void first_page() noexcept;
    void last_page() noexcept;
    void rotate_x(const std::int32_t rotation) noexcept;
    void change_double_page() noexcept;
    void change_manga_mode() noexcept;
    void change_fullscreen() noexcept;
    void displayed_double() noexcept;

    void update_page_information() noexcept;
    bool get_virtual_double_page(const std::optional<page_t> query = std::nullopt) noexcept;

    void on_file_opened() noexcept;
    void on_file_closed() noexcept;

    void page_available(const page_t page) noexcept;

    void add_shortcuts() noexcept;

    void on_bookmark_add() noexcept;
    void on_bookmark_manager() noexcept;

    void on_exit() noexcept;
    void on_escape_event() noexcept;
    void on_open_page_extractor() noexcept;
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

    std::array<std::int32_t, 2> get_visible_area_size() noexcept;

    std::shared_ptr<config::settings> settings = std::make_shared<config::settings>();
    std::shared_ptr<gui::lib::view_state> view_state = std::make_shared<gui::lib::view_state>();

    std::shared_ptr<vfs::file_handler> file_handler_ =
        std::make_shared<vfs::file_handler>(this->settings, this->view_state);

    std::shared_ptr<vfs::bookmarks> bookmarks_ = std::make_shared<vfs::bookmarks>();

    bool waiting_for_redraw_{false};

    std::array<std::filesystem::path, 2> current_images_;

    Gtk::Box box_;
    Gtk::Box center_box_;

    gui::menubar menubar_ = gui::menubar();
    gui::thumbbar thumb_sidebar_ = gui::thumbbar(this->settings);
    gui::viewport viewport_ = gui::viewport(this->settings);
    gui::statusbar statusbar_ = gui::statusbar(this->settings, this->view_state);
};
} // namespace gui
