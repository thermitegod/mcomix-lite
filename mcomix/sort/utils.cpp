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
#include <string>
#include <string_view>

#include "sort/utils.hpp"

/**
 * @brief rpartition
 *
 * - Split the string at the last occurrence of sep
 *
 * @param[in] str The string to be split
 * @param[in] sep The string to be split at
 *
 * @return A 3 element array containing the part before the separator,
 * the separator itself, and the part after the separator. If the
 * separator is not found, return a 3 element array containing
 * two empty strings, followed by the string itself.
 */
[[nodiscard]] inline std::array<std::string, 3>
rpartition(const std::string_view str, const std::string_view sep) noexcept
{
    using namespace std::string_literals;

    if (sep.empty())
    {
        return {""s, ""s, std::string{str.cbegin(), str.cend()}};
    }

    const auto pos = str.rfind(sep);
    if (pos == std::string_view::npos)
    {
        return {""s, ""s, std::string{str.cbegin(), str.cend()}};
    }

    return {std::string(str.substr(0, pos)), std::string(sep), std::string(str.substr(pos + sep.size()))};
}

utils::split_basename_extension_data
utils::split_basename_extension(const std::filesystem::path& filename) noexcept
{
    if (std::filesystem::is_directory(filename))
    {
        return {filename.string(), "", false};
    }

    // Find the last dot in the filename
    const auto dot_pos = filename.string().find_last_of('.');

    // Check if the dot is not at the beginning or end of the filename
    if (dot_pos != std::string::npos && dot_pos != 0 && dot_pos != filename.string().length() - 1)
    {
        const auto split = rpartition(filename.string(), ".");

        // Check if the extension is a compressed tar archive
        if (split[0].ends_with(".tar"))
        {
            // Find the second last dot in the filename
            const auto split_second = rpartition(split[0], ".");

            return {split_second[0], std::format(".{}.{}", split_second[2], split[2]), true};
        }
        else
        {
            // Return the basename and the extension
            return {split[0], std::format(".{}", split[2]), false};
        }
    }

    // No valid extension found, return the whole filename as the basename
    return {filename.string(), "", false};
}
