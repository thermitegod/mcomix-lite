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

#include <algorithm>
#include <array>
#include <filesystem>
#include <string_view>

#include "vfs/file-supported.hxx"

bool
vfs::is_archive(const std::filesystem::path& filename) noexcept
{
    static constexpr std::array<std::string_view, 8> extensions{
        ".zip",
        ".7z",
        ".rar",
        ".tar",
        ".cbz",
        ".cb7",
        ".cbr",
        ".cbt",
    };

    return std::ranges::any_of(extensions,
                               [&filename](const std::string_view ext)
                               { return filename.extension().string().contains(ext); });
}

bool
vfs::is_image(const std::filesystem::path& filename) noexcept
{
    static constexpr std::array<std::string_view, 27> extensions{
        ".tga",   ".svgz", ".pbm",  ".svg", ".jpeg",   ".icns", ".ani", ".ppm", ".bmp",
        ".targa", ".tif",  ".pnm",  ".gif", ".svg.gz", ".pgm",  ".jpe", ".ico", ".qif",
        ".jpg",   ".xpm",  ".tiff", ".png", ".xbm",    ".qtif", ".jxl", ".cur", ".webp",
    };

    return std::ranges::any_of(extensions,
                               [&filename](const std::string_view ext)
                               { return filename.extension().string().contains(ext); });
}
