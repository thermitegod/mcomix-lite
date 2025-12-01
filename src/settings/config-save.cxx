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

#include <glaze/glaze.hpp>

#include <magic_enum/magic_enum.hpp>

#include <ztd/extra/glaze.hxx>
#include <ztd/ztd.hxx>

#include "settings/config.hxx"
#include "settings/settings.hxx"

#include "logger.hxx"

[[nodiscard]] static config::settings
pack_settings(const std::shared_ptr<config::settings>& settings) noexcept
{
    config::settings s;

    // clang-format off
    s.default_double_page = settings->default_double_page;
    s.default_manga_mode = settings->default_manga_mode;
    s.page_ff_step = settings->page_ff_step;
    s.virtual_double_page_for_fitting_images = settings->virtual_double_page_for_fitting_images;
    s.double_step_in_double_page_mode = settings->double_step_in_double_page_mode;
    s.double_page_center_space = settings->double_page_center_space;
    s.thumbnail_size = settings->thumbnail_size;
    s.keep_transformation = settings->keep_transformation;
    s.rotation = settings->rotation;
    s.si_units = settings->si_units;
    s.move_file = settings->move_file;

    s.bookmark_manager_fullpath = settings->bookmark_manager_fullpath;

    s.hide_thumbar = settings->hide_thumbar;
    s.hide_menubar = settings->hide_menubar;
    s.hide_statusbar = settings->hide_statusbar;

    s.fullscreen.hide_thumbar = settings->fullscreen.hide_thumbar;
    s.fullscreen.hide_menubar = settings->fullscreen.hide_menubar;
    s.fullscreen.hide_statusbar = settings->fullscreen.hide_statusbar;

    s.statusbar.page_numbers = settings->statusbar.page_numbers;
    s.statusbar.file_numbers = settings->statusbar.file_numbers;
    s.statusbar.page_resolution = settings->statusbar.page_resolution;
    s.statusbar.page_resolution_zoom_scale = settings->statusbar.page_resolution_zoom_scale;
    s.statusbar.archive_filename = settings->statusbar.archive_filename;
    s.statusbar.archive_filename_fullpath = settings->statusbar.archive_filename_fullpath;
    s.statusbar.page_filename = settings->statusbar.page_filename;
    s.statusbar.page_filesize = settings->statusbar.page_filesize;
    s.statusbar.archive_filesize = settings->statusbar.archive_filesize;
    s.statusbar.view_mode = settings->statusbar.view_mode;
    // clang-format on

    return s;
}

void
config::save(const std::filesystem::path& path,
             const std::shared_ptr<config::settings>& settings) noexcept
{
    if (!std::filesystem::exists(path))
    {
        std::filesystem::create_directory(path);
    }

    const auto config_data =
        config_file_data{config::disk_format::version, pack_settings(settings)};

    std::string buffer;
    // TODO prettify=true segfaults when used in Gtk::Window destructor,
    // it was not doing it earlier need to investigate.
    // std::basic_string<char>::operator[](size_type): Assertion '__pos <= size()' failed.
    const auto ec =
        glz::write_file_json<glz::opts{.prettify = false}>(config_data,
                                                           (path / config::filename).c_str(),
                                                           buffer);

    logger::error_if(ec, "Failed to write config file: {}", glz::format_error(ec, buffer));
}
