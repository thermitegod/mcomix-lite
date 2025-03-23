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

#include <filesystem>
#include <string>

namespace utils
{
struct split_basename_extension_data final
{
    std::string basename;
    std::string extension;
    bool is_multipart_extension;
};
/**
 * Split a filename into its basename and extension,
 * unlike using std::filesystem::path::filename/std::filesystem::path::extension
 * this will support multi part extensions such as .tar.gz,.tar.zst,etc..
 * will not set an extension if the filename is a directory.
 */
[[nodiscard]] split_basename_extension_data split_basename_extension(const std::filesystem::path& filename) noexcept;
} // namespace utils
