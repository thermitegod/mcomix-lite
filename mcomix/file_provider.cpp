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
#include <filesystem>
#include <utility>
#include <vector>

#include "sort/sort.hpp"

#include "file_provider.hpp"
#include "supported.hpp"

file_provider::file_provider(const std::vector<std::filesystem::path>& filelist)
{
    if (filelist.empty())
    {
        return;
    }

    this->files_ = filelist;

    // Open the first file from the command line,
    // also sets the mode based on file type.
    const auto& open_file = filelist.front();

    this->base_dir_ = std::filesystem::is_directory(open_file) ? open_file : open_file.parent_path();

    if (filelist.size() == 1)
    {
        // Browse mode: open all files in dir
        this->open_mode_ = open_mode::browse;
    }
    else
    {
        // Predefined mode: Only open files passed from command line
        this->open_mode_ = open_mode::predefined;
    }
}

void
file_provider::sort_files(const FileSortType sort_type, const FileSortDirection sort_direction) noexcept
{
    if (this->files_.empty())
    {
        return;
    }

    switch (sort_type)
    {
        case FileSortType::NONE:
            // No sorting
            break;
        case FileSortType::SIZE:
        case FileSortType::LAST_MODIFIED:
        case FileSortType::NAME:
            this->files_ = sort_alphanumeric(this->files_);
            break;
        case FileSortType::NAME_LITERAL:
            std::ranges::sort(this->files_);
            break;
    }

    if (sort_direction == FileSortDirection::DESCENDING)
    {
        std::ranges::reverse(this->files_);
    }
}

std::vector<std::filesystem::path>
file_provider::list_files(const FileTypes mode, const FileSortType sort_type,
                          const FileSortDirection sort_direction) noexcept
{
    auto should_accept = [](const std::filesystem::path& file, const FileTypes mode) -> bool
    {
        switch (mode)
        {
            case FileTypes::ARCHIVES:
                return is_archive(file);
            case FileTypes::IMAGES:
                return is_image(file);
        }
        std::unreachable();
    };

    std::vector<std::filesystem::path> filelist;

    switch (this->open_mode_)
    {
        case open_mode::browse:
            for (const auto& dfile : std::filesystem::directory_iterator(this->base_dir_))
            {
                if (dfile.is_directory())
                {
                    continue;
                }

                const auto& file = dfile.path();

                if (should_accept(file, mode))
                {
                    filelist.push_back(file);
                }
            }
            this->files_ = filelist;
            this->sort_files(sort_type, sort_direction);
            break;
        case open_mode::predefined:
            for (const auto& file : this->files_)
            {
                if (std::filesystem::is_directory(file))
                {
                    continue;
                }

                if (!std::filesystem::exists(file))
                {
                    continue;
                }

                if (should_accept(file, mode))
                {
                    filelist.push_back(file);
                }
            }
            this->files_ = filelist;
            break;
        case open_mode::none:
            break;
    }

    return this->files_;
}
