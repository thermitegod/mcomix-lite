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
#include <flat_set>
#include <string_view>

#include <gdkmm.h>
#include <glibmm.h>

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
                               { return filename.extension() == ext; });
}

bool
vfs::is_image(const std::filesystem::path& filename) noexcept
{
    static const auto extensions = std::invoke(
        []()
        {
            using namespace std::string_literals;
            std::flat_set<std::string> extensions;
            for (const auto& format : Gdk::Pixbuf::get_formats())
            {
                for (const auto& ext : format.get_extensions())
                {
                    extensions.emplace("."s += ext.data());
                }
            }
            // std::println("{}", extensions);
            return extensions;
        });

    return std::ranges::any_of(extensions,
                               [&filename](const std::string_view ext)
                               { return filename.extension() == ext; });
}
