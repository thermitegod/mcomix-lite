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
#include <flat_map>
#include <span>

namespace vfs
{
class image_files
{
  public:
    void set_image_files(const std::span<const std::filesystem::path> filelist) noexcept;
    void cleanup() noexcept;

    [[nodiscard]] std::int32_t total_pages() const noexcept;
    [[nodiscard]] const std::filesystem::path
    path_from_page(const std::int32_t page) const noexcept;
    [[nodiscard]] std::int32_t page_from_path(const std::filesystem::path& path) const noexcept;

  private:
    std::flat_map<std::filesystem::path, std::int32_t> pages_;
    std::flat_map<std::int32_t, std::filesystem::path> paths_;
    std::int32_t total_pages_{0};
};
} // namespace vfs
