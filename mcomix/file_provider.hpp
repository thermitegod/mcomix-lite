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
#include <vector>

#include <cstdint>

#include "enums.hpp"

class file_provider
{
  public:
    file_provider() = default;
    file_provider(const std::vector<std::filesystem::path>& filelist);

    [[nodiscard]] std::vector<std::filesystem::path> list_files(const FileTypes mode, const FileSortType sort_type,
                                                                const FileSortDirection sort_direction) noexcept;

  private:
    void sort_files(const FileSortType sort_type, const FileSortDirection sort_direction) noexcept;

    enum class open_mode : std::uint8_t
    {
        none,
        browse,
        predefined,
    };

    open_mode open_mode_ = open_mode::none;

    std::vector<std::filesystem::path> files_;
    std::filesystem::path base_dir_;
};
