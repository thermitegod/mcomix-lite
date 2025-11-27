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

#include <filesystem>
#include <ranges>
#include <span>

#include <cassert>

#include "vfs/image-files.hxx"

#include "types.hxx"

void
vfs::image_files::set_image_files(const std::span<const std::filesystem::path> filelist) noexcept
{
    assert(!filelist.empty());
    assert(this->pages_.empty());
    assert(this->paths_.empty());

    for (const auto [idx, file] : std::ranges::views::enumerate(filelist))
    {
        this->pages_.insert({file, idx + 1});
        this->paths_.insert({idx + 1, file});
    }
    this->total_pages_ = static_cast<page_t>(filelist.size());
}

void
vfs::image_files::cleanup() noexcept
{
    this->pages_.clear();
    this->paths_.clear();
    this->total_pages_ = 0;
}

page_t
vfs::image_files::total_pages() const noexcept
{
    return this->total_pages_;
}

const std::filesystem::path
vfs::image_files::path_from_page(const page_t page) const noexcept
{
    return this->paths_.at(page);
}

page_t
vfs::image_files::page_from_path(const std::filesystem::path& path) const noexcept
{
    return this->pages_.at(path);
}
