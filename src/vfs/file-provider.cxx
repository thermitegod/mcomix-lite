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
#include <span>
#include <utility>
#include <vector>

#include "vfs/utils/sort.hxx"

#include "file-provider.hxx"
#include "file-supported.hxx"

vfs::file_provider::file_provider(const std::span<const std::filesystem::path> files) noexcept
    : files_(files.cbegin(), files.cend())
{
    if (files.empty())
    {
        return;
    }

    // Open the first file, before sorting, from the command line.
    // also sets the mode based on file type.
    const auto& open_file = this->files_.front();

    this->base_dir_ =
        std::filesystem::is_directory(open_file) ? open_file : open_file.parent_path();

    if (files.size() == 1)
    {
        // Browse mode: open all files in dir
        this->open_mode_ = open_mode::browse;
    }
    else
    {
        // Predefined mode: Only open files passed from the commandline, in order passed
        this->open_mode_ = open_mode::predefined;
    }
}

void
vfs::file_provider::sort_files() noexcept
{
    if (this->files_.empty())
    {
        return;
    }

    vfs::utils::sort_alphanumeric(this->files_);
}

std::span<const std::filesystem::path>
vfs::file_provider::list_files(const vfs::file_provider::file_type mode) noexcept
{
    auto should_accept = [](const std::filesystem::path& file,
                            const vfs::file_provider::file_type mode) -> bool
    {
        if (mode == vfs::file_provider::file_type::archives)
        {
            return vfs::is_archive(file);
        }
        else if (mode == vfs::file_provider::file_type::images)
        {
            return vfs::is_image(file);
        }
        std::unreachable();
    };

    if (!std::filesystem::exists(this->base_dir_))
    {
        return {};
    }

    if (this->open_mode_ == open_mode::browse)
    {
        this->files_.clear();
        for (const auto& dfile : std::filesystem::directory_iterator(this->base_dir_))
        {
            if (dfile.is_directory())
            {
                continue;
            }

            const auto& file = dfile.path();

            if (should_accept(file, mode))
            {
                this->files_.push_back(file);
            }
        }
        this->sort_files();
    }
    else if (this->open_mode_ == open_mode::predefined)
    {
        std::vector<std::filesystem::path> filelist;
        for (const auto& file : this->files_)
        {
            if (std::filesystem::is_directory(file))
            {
                continue;
            }

            if (should_accept(file, mode))
            {
                filelist.push_back(file);
            }
        }
        this->files_ = filelist;
    }

    return this->files_;
}
