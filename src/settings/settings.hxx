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

#include <glibmm.h>

#include "types.hxx"

namespace config
{
enum double_page
{
    never,
    as_one_title,
    as_one_wide,
    always,
};

struct settings final
{
    bool default_double_page = true;
    bool default_manga_mode = true;
    page_t page_ff_step = 10;
    double_page virtual_double_page_for_fitting_images = double_page::always;
    bool double_step_in_double_page_mode = true;
    bool double_page_center_space = true;
    std::int32_t thumbnail_size = 80;
    bool keep_transformation = false;
    std::int32_t rotation = 0;
    bool si_units = false;
    std::string move_file = "keep";
    bool confirm_archive_change = false;

    std::int32_t cache_forward = 5;
    std::int32_t cache_behind = 5;

    bool bookmark_manager_fullpath = true;

    bool hide_thumbar = false;
    bool hide_menubar = false;
    bool hide_statusbar = false;

    struct fullscreen
    {
        bool hide_thumbar = false;
        bool hide_menubar = true;
        bool hide_statusbar = true;
    } fullscreen;

    struct statusbar
    {
        bool page_numbers = true;
        bool file_numbers = true;
        bool page_resolution = true;
        bool page_resolution_zoom_scale = true;
        bool archive_filename = true;
        bool archive_filename_fullpath = true;
        bool page_filename = true;
        bool page_filesize = true;
        bool archive_filesize = true;
        bool view_mode = true;
    } statusbar;
};
} // namespace config
