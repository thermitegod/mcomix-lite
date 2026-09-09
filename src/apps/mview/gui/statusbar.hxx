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
#include <span>
#include <string>
#include <string_view>

#include <cstdint>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include "settings.hxx"

namespace gui
{
class statusbar : public Gtk::Box
{
  public:
    explicit statusbar(const std::shared_ptr<config::settings>& settings) noexcept;

    void set_message(std::string_view message) noexcept;
    void set_page_number(const std::int32_t page, const std::int32_t total_pages) noexcept;
    void set_resolution(const std::array<std::int32_t, 2> scaled_size,
                        const std::array<std::int32_t, 2> size_list) noexcept;
    void set_archive_filename(const std::filesystem::path& filename) noexcept;
    void set_filename(std::string filename) noexcept;
    void set_filesize(std::string filesize) noexcept;

    void update() noexcept;

  protected:
    Gtk::Label statusbar_;

  private:
    std::shared_ptr<config::settings> settings;

    const std::string sep_ = "  |  ";

    std::string total_page_numbers_;
    std::string page_resolution_;
    std::string archive_filename_;
    std::string page_filename_;
    std::string page_filesize_;
    std::string image_scaling_;
};
} // namespace gui
