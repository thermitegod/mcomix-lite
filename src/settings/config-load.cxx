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
#include <string>

#include <glaze/glaze.hpp>

#include <magic_enum/magic_enum.hpp>

#include <ztd/extra/glaze.hxx>
#include <ztd/ztd.hxx>

#include "settings/config.hxx"
#include "settings/settings.hxx"

#include "logger.hxx"

static void
parse_settings(const u64 version, const config::settings& loaded,
               const std::shared_ptr<config::settings>& settings) noexcept
{
    (void)version;

    // clang-format off
    settings->default_double_page = loaded.default_double_page;
    settings->fullscreen_hide_menubar = loaded.fullscreen_hide_menubar;
    settings->fullscreen_hide_statusbar = loaded.fullscreen_hide_statusbar;
    settings->default_manga_mode = loaded.default_manga_mode;
    settings->page_ff_step = loaded.page_ff_step;
    settings->virtual_double_page_for_fitting_images = loaded.virtual_double_page_for_fitting_images;
    settings->double_step_in_double_page_mode = loaded.double_step_in_double_page_mode;
    settings->double_page_center_space = loaded.double_page_center_space;
    settings->thumbnail_size = loaded.thumbnail_size;
    settings->keep_transformation = loaded.keep_transformation;
    settings->rotation = loaded.rotation;
    settings->si_units = loaded.si_units;
    settings->move_file = loaded.move_file;

    settings->statusbar.page_numbers = loaded.statusbar.page_numbers;
    settings->statusbar.file_numbers = loaded.statusbar.file_numbers;
    settings->statusbar.page_resolution = loaded.statusbar.page_resolution;
    settings->statusbar.page_resolution_zoom_scale = loaded.statusbar.page_resolution_zoom_scale;
    settings->statusbar.archive_filename = loaded.statusbar.archive_filename;
    settings->statusbar.archive_filename_fullpath = loaded.statusbar.archive_filename_fullpath;
    settings->statusbar.page_filename = loaded.statusbar.page_filename;
    settings->statusbar.page_filesize = loaded.statusbar.page_filesize;
    settings->statusbar.archive_filesize = loaded.statusbar.archive_filesize;
    settings->statusbar.view_mode = loaded.statusbar.view_mode;
    // clang-format on
}

void
config::load(const std::filesystem::path& path,
             const std::shared_ptr<config::settings>& settings) noexcept
{
    if (!std::filesystem::exists(path / config::filename))
    {
        return;
    }

    config_file_data config_data;
    std::string buffer;
    const auto ec = glz::read_file_json<glz::opts{.error_on_unknown_keys = false}>(
        config_data,
        (path / config::filename).c_str(),
        buffer);

    if (ec)
    {
        logger::error("Failed to load config file: {}", glz::format_error(ec, buffer));
        return;
    }

    parse_settings(config_data.version, config_data.settings, settings);
}
