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

#include "types.hxx"

namespace vfs
{
class image_files
{
  public:
    void set_image_files(const std::span<const std::filesystem::path> filelist) noexcept;
    void cleanup() noexcept;

    [[nodiscard]] page_t total_pages() const noexcept;
    [[nodiscard]] const std::filesystem::path path_from_page(const page_t page) const noexcept;
    [[nodiscard]] page_t page_from_path(const std::filesystem::path& path) const noexcept;

  private:
    std::flat_map<std::filesystem::path, page_t> pages_;
    std::flat_map<page_t, std::filesystem::path> paths_;
    page_t total_pages_{0};
};
} // namespace vfs
