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
#include <format>
#include <string>

#include <glaze/glaze.hpp>

#include <ztd/extra/glaze.hxx>
#include <ztd/ztd.hxx>

#include "vfs/bookmarks.hxx"
#include "vfs/user-dirs.hxx"

#include "logger.hxx"

namespace bookmark_disk_format
{
constexpr u64 version = 1_u64;
const std::filesystem::path path = vfs::program::data() / "bookmarks.json";

struct bookmark_data final
{
    u64 version;
    std::vector<vfs::bookmarks::bookmark_data> bookmarks;
};
} // namespace bookmark_disk_format

void
vfs::bookmarks::save() noexcept
{
    if (!std::filesystem::exists(vfs::program::data()))
    {
        std::filesystem::create_directory(vfs::program::data());
    }

    const auto data =
        bookmark_disk_format::bookmark_data{bookmark_disk_format::version, this->bookmarks_};

    std::string buffer;
    const auto ec =
        glz::write_file_json<glz::opts{.prettify = true}>(data,
                                                          bookmark_disk_format::path.c_str(),
                                                          buffer);

    if (ec)
    {
        this->signal_save_error().emit(glz::format_error(ec, buffer));
        logger::error("Failed to write bookmark file: {}", glz::format_error(ec, buffer));
    }
}

void
vfs::bookmarks::load() noexcept
{
    if (!std::filesystem::exists(bookmark_disk_format::path))
    {
        return;
    }

    bookmark_disk_format::bookmark_data config_data;
    std::string buffer;
    const auto ec = glz::read_file_json<glz::opts{.error_on_unknown_keys = false}>(
        config_data,
        bookmark_disk_format::path.c_str(),
        buffer);

    if (ec)
    {
        this->signal_load_error().emit(glz::format_error(ec, buffer));
        logger::error("Failed to load bookmark file: {}", glz::format_error(ec, buffer));
        return;
    }

    this->bookmarks_ = config_data.bookmarks;
}

void
vfs::bookmarks::add(const bookmark_data& new_bookmark) noexcept
{
    // TODO only reload if mtime has changed
    this->load();

    for (auto& bookmark : this->bookmarks_)
    {
        if (bookmark.path == new_bookmark.path)
        {
            bookmark.current_page = new_bookmark.current_page;
            bookmark.total_pages = new_bookmark.total_pages;
            bookmark.created = new_bookmark.created;
            this->save();
            return;
        }
    }

    this->bookmarks_.push_back(new_bookmark);
    this->save();
}

void
vfs::bookmarks::remove(const std::filesystem::path& path) noexcept
{
    // TODO only reload if mtime has changed
    this->load();

    std::erase_if(this->bookmarks_,
                  [&path](const bookmark_data& bookmark) { return bookmark.path == path; });

    this->save();
}

std::span<const vfs::bookmarks::bookmark_data>
vfs::bookmarks::get_bookmarks() noexcept
{
    // TODO only reload if mtime has changed
    this->load();

    return this->bookmarks_;
}
