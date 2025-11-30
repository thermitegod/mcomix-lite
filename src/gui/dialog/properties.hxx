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

#include <filesystem>
#include <memory>

#include <gtkmm.h>

#include "vfs/file-handler.hxx"

namespace gui::dialog
{
class properties : public Gtk::ApplicationWindow
{
  public:
    properties(Gtk::ApplicationWindow& parent,
               const std::shared_ptr<vfs::file_handler>& file_handler,
               const std::shared_ptr<gui::lib::view_state>& view_state,
               const std::shared_ptr<config::settings>& settings);

  private:
    bool on_key_press(std::uint32_t keyval, std::uint32_t keycode,
                      Gdk::ModifierType state) noexcept;
    void on_button_close_clicked() noexcept;

    void init_archive_tab() noexcept;
    void init_image_tab(const page_t page, std::string_view label) noexcept;

    std::vector<std::array<std::string, 2>>
    secondary_info(const std::filesystem::path& path) noexcept;

    Gtk::Box box_;
    Gtk::Notebook notebook_;

    Gtk::Box button_box_;
    Gtk::Button button_close_;

    std::shared_ptr<vfs::file_handler> file_handler_;
    std::shared_ptr<gui::lib::view_state> view_state_;
    std::shared_ptr<config::settings> settings_;
};
} // namespace gui::dialog
