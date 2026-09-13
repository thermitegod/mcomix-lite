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

#include <string>

#include <cstdint>

#include "settings/property.hxx"

#include "bitflags/bitflags.hxx"

namespace config
{
enum class double_page : std::uint32_t
{
    never = 0,
    first_page = 1 << 0,
    wide_page = 1 << 1,
    always = first_page | wide_page,
};

struct settings final
{
    bool default_double_page = true;
    bool default_manga_mode = true;
    std::int32_t page_ff_step = 10;
    bit_flags<double_page> virtual_double_page_mode{double_page::always};
    bool double_page_change = true;
    bool double_page_center_space = true;
    std::int32_t thumbnail_size = 80;
    bool keep_transformation = false;
    std::int32_t rotation = 0;
    bool si_units = false;
    std::string move_file = "keep";
    bool confirm_archive_change = false;

    bool bookmark_manager_fullpath = true;

    bool hide_thumbar = false;
    bool hide_menubar = false;
    bool hide_statusbar = false;

    struct fullscreen_t
    {
        bool hide_thumbar = false;
        bool hide_menubar = true;
        bool hide_statusbar = true;
    } fullscreen;

    struct statusbar_t
    {
        Property<bool> page_numbers = true;
        Property<bool> file_numbers = true;
        Property<bool> page_resolution = true;
        bool page_resolution_zoom_scale = true;
        Property<bool> archive_filename = true;
        bool archive_filename_fullpath = true;
        Property<bool> page_filename = true;
        Property<bool> page_filesize = true;
        Property<bool> archive_filesize = true;
        Property<bool> view_mode = true;
    } statusbar;
};
} // namespace config
