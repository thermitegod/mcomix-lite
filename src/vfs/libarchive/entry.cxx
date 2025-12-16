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

#include <expected>
#include <filesystem>
#include <fstream>
#include <string>
#include <system_error>

#include <cstdint>

#include <archive.h>

#include "entry.hxx"

namespace vfs::libarchive
{
entry::entry(archive_entry* entry, const std::shared_ptr<archive>& archive) noexcept
    : entry_(entry, [](archive_entry*) { /* do nothing */ }), archive_(archive)
{
}

std::expected<void, std::error_code>
entry::extract(const std::filesystem::path& path) noexcept
{
    constexpr auto BUFFER_SIZE = 16384;

    if (!std::filesystem::exists(path.parent_path()))
    {
        std::error_code ec;
        std::filesystem::create_directories(path.parent_path(), ec);
        if (ec)
        {
            return std::unexpected(ec);
        }
    }

    std::ofstream file(path, std::ios::binary);
    if (!file.is_open())
    {
        return std::unexpected(std::make_error_code(std::errc::permission_denied));
    }

    std::array<char, BUFFER_SIZE> buffer;
    while (true)
    {
        const auto size = archive_read_data(this->archive_.get(), buffer.data(), buffer.size());
        if (size < 0)
        {
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }

        if (size == 0)
        { // EOF
            break;
        }

        file.write(buffer.data(), static_cast<std::streamsize>(size));
        if (!file)
        {
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }
    }

    return {};
}

int64_t
entry::get_gid() const noexcept
{
    return archive_entry_gid(this->entry_.get());
}

int64_t
entry::get_ino() const noexcept
{
    return archive_entry_ino(this->entry_.get());
}

int64_t
entry::get_ino64() const noexcept
{
    return archive_entry_ino64(this->entry_.get());
}

int64_t
entry::get_size() const noexcept
{
    return archive_entry_size(this->entry_.get());
}

int64_t
entry::get_uid() const noexcept
{
    return archive_entry_uid(this->entry_.get());
}

mode_t
entry::get_mode() const noexcept
{
    return archive_entry_mode(this->entry_.get());
}

mode_t
entry::get_perm() const noexcept
{
    return archive_entry_perm(this->entry_.get());
}

dev_t
entry::get_rdev() const noexcept
{
    return archive_entry_rdev(this->entry_.get());
}

dev_t
entry::get_rdevmajor() const noexcept
{
    return archive_entry_rdevmajor(this->entry_.get());
}

dev_t
entry::get_rdevminor() const noexcept
{
    return archive_entry_rdevminor(this->entry_.get());
}

std::string
entry::get_hardlink() const noexcept
{
    return archive_entry_hardlink(this->entry_.get());
}

std::string
entry::get_pathname() const noexcept
{
    return archive_entry_pathname(this->entry_.get());
}

std::string
entry::get_symlink() const noexcept
{
    return archive_entry_symlink(this->entry_.get());
}

std::string
entry::get_user_name() const noexcept
{
    return archive_entry_uname(this->entry_.get());
}

std::string
entry::get_group_name() const noexcept
{
    return archive_entry_gname(this->entry_.get());
}

std::uint32_t
entry::get_nlink() const noexcept
{
    return archive_entry_nlink(this->entry_.get());
}
} // namespace vfs::libarchive
