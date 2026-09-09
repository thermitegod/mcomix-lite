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

#include <array>
#include <filesystem>
#include <format>
#include <span>
#include <string_view>

#include <cstdint>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include <ztd/ztd.hxx>

#include "gui/statusbar.hxx"

#include "vfs/utils/utils.hxx"

#include "settings.hxx"

gui::statusbar::statusbar(const std::shared_ptr<config::settings>& settings) noexcept
    : settings(settings)
{
    set_halign(Gtk::Align::START);
    set_valign(Gtk::Align::END);
    set_hexpand(true);
    set_vexpand(false);

    statusbar_.set_margin_top(5);
    statusbar_.set_margin_bottom(5);
    statusbar_.set_ellipsize(Pango::EllipsizeMode::END);
    statusbar_.set_hexpand(true);
    statusbar_.set_halign(Gtk::Align::START);
    append(statusbar_);
}

void
gui::statusbar::set_message(std::string_view message) noexcept
{
    statusbar_.set_label(std::format("    {}", message));
}

void
gui::statusbar::set_page_number(const std::int32_t page, const std::int32_t total_pages) noexcept
{
    total_page_numbers_ = std::format("{} / {}", page, total_pages);
}

void
gui::statusbar::set_resolution(std::array<std::int32_t, 2> scaled_size,
                               std::array<std::int32_t, 2> size_list) noexcept
{
    const std::int32_t x = size_list[0];
    const std::int32_t y = size_list[1];
    const double scale = static_cast<double>(scaled_size[0]) / size_list[0];

    std::string page_resolution;
    if (settings->statusbar.page_resolution_zoom_scale)
    {
        page_resolution.append(std::format("{}x{} ({:.2f}%), ", x, y, scale * 100));
    }
    else
    {
        page_resolution.append(std::format("{}x{}, ", x, y));
    }

    page_resolution_ = ztd::rstrip(page_resolution, ", ");
}

void
gui::statusbar::set_archive_filename(const std::filesystem::path& filename) noexcept
{
    archive_filename_ = std::format("{}", filename);
}

void
gui::statusbar::set_filename(std::string filename) noexcept
{
    page_filename_ = filename;
}

void
gui::statusbar::set_filesize(std::string filesize) noexcept
{
    page_filesize_ = filesize;
}

void
gui::statusbar::update() noexcept
{
    std::string text;

    if (settings->statusbar.page_numbers)
    {
        text.append(std::format("{}{}", total_page_numbers_, sep_));
    }
    if (settings->statusbar.page_resolution)
    {
        text.append(std::format("{}{}", page_resolution_, sep_));
    }
    if (settings->statusbar.archive_filename)
    {
        text.append(std::format("{}{}", archive_filename_, sep_));
    }
    if (settings->statusbar.page_filename)
    {
        text.append(std::format("{}{}", page_filename_, sep_));
    }
    if (settings->statusbar.page_filesize)
    {
        text.append(std::format("{}{}", page_filesize_, sep_));
    }

    set_message(ztd::rstrip(text, sep_));
}
