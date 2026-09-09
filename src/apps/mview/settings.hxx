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

namespace config
{
struct settings final
{
    bool keep_transformation = false;
    std::int32_t rotation = 0;
    bool si_units = false;
    std::string move_file = "keep";

    bool hide_menubar = false;
    bool hide_statusbar = false;

    struct fullscreen_t
    {
        bool hide_menubar = true;
        bool hide_statusbar = true;
    } fullscreen;

    struct statusbar_t
    {
        bool page_numbers = true;
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
