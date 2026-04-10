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

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include <ztd/ztd.hxx>

#include "settings/settings.hxx"

#include "gui/statusbar.hxx"

#include "gui/lib/view-state.hxx"

#include "vfs/utils/utils.hxx"

gui::statusbar::statusbar(const std::shared_ptr<config::settings>& settings,
                          const std::shared_ptr<gui::lib::view_state>& view_state) noexcept
    : settings(settings), view_state(view_state)
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
gui::statusbar::set_message(const std::string_view message) noexcept
{
    statusbar_.set_label(std::format("    {}", message));
}

void
gui::statusbar::set_page_number(const page_t page, const std::int32_t total_pages) noexcept
{
    std::string p;
    if (view_state->is_displaying_double())
    {
        if (view_state->is_manga_mode())
        {
            p = std::format("{}, {}", page + 1, page);
        }
        else
        {
            p = std::format("{}, {}", page, page + 1);
        }
    }
    else
    {
        p = std::format("{}", page);
    }

    total_page_numbers_ = std::format("{} / {}", p, total_pages);
}

void
gui::statusbar::set_view_mode() noexcept
{
    if (view_state->is_manga_mode())
    {
        current_view_mode_ = "Manga";
    }
    else
    {
        current_view_mode_ = "Western";
    }
}

void
gui::statusbar::set_file_number(std::int32_t file_number, std::int32_t total) noexcept
{
    total_file_numbers_ = std::format("{} / {}", file_number, total);
}

void
gui::statusbar::set_resolution(std::vector<std::array<std::int32_t, 2>> scaled_sizes,
                               std::vector<std::array<std::int32_t, 2>> size_list) noexcept
{
    std::vector<std::tuple<std::int32_t, std::int32_t, double>> resolutions;
    resolutions.reserve(scaled_sizes.size());

    for (std::size_t i = 0; i < scaled_sizes.size(); ++i)
    {
        const auto& scaled_size = scaled_sizes[i];
        const auto& size = size_list[i];
        const double scale = static_cast<double>(scaled_size[0]) / size[0];
        resolutions.emplace_back(size[0], size[1], scale);
    }

    if (view_state->is_manga_mode())
    {
        std::ranges::reverse(resolutions);
    }

    std::string page_resolution;
    for (const auto& [x, y, scale] : resolutions)
    {
        if (settings->statusbar.page_resolution_zoom_scale)
        {
            page_resolution.append(std::format("{}x{} ({:.2f}%), ", x, y, scale * 100));
        }
        else
        {
            page_resolution.append(std::format("{}x{}, ", x, y));
        }
    }

    page_resolution_ = ztd::rstrip(page_resolution, ", ");
}

void
gui::statusbar::set_archive_filename(const std::filesystem::path& filename) noexcept
{
    archive_filename_ = filename.string();
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
gui::statusbar::set_filesize_archive(const std::filesystem::path& filename) noexcept
{
    if (std::filesystem::is_directory(filename))
    {
        archive_filesize_ = "0 B";
    }
    else
    {
        archive_filesize_ = vfs::utils::file_size(filename, settings->si_units);
    }
}

void
gui::statusbar::update() noexcept
{
    std::string text;

    if (settings->statusbar.page_numbers)
    {
        text.append(std::format("{}{}", total_page_numbers_, sep_));
    }
    if (settings->statusbar.file_numbers)
    {
        text.append(std::format("{}{}", total_file_numbers_, sep_));
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
    if (settings->statusbar.archive_filesize)
    {
        text.append(std::format("{}{}", archive_filesize_, sep_));
    }
    if (settings->statusbar.view_mode)
    {
        text.append(std::format("{}{}", current_view_mode_, sep_));
    }

    set_message(ztd::rstrip(text, sep_));
}
