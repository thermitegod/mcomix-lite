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

#include "vfs/utils/utils.hxx"

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
gui::statusbar::set_page_number(const std::int32_t total_pages) noexcept
{
    total_page_numbers_ = std::format("{}", total_pages);
}

void
gui::statusbar::set_file_number(std::int32_t file_number, std::int32_t total) noexcept
{
    total_file_numbers_ = std::format("{} / {}", file_number, total);
}

void
gui::statusbar::set_archive_filename(const std::filesystem::path& filename) noexcept
{
    archive_filename_ = std::format("{}", filename);
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
    if (settings->statusbar.archive_filename)
    {
        text.append(std::format("{}{}", archive_filename_, sep_));
    }
    if (settings->statusbar.archive_filesize)
    {
        text.append(std::format("{}{}", archive_filesize_, sep_));
    }

    set_message(ztd::rstrip(text, sep_));
}
