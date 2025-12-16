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

#include <expected>
#include <filesystem>
#include <memory>
#include <string>
#include <system_error>

#include <cstdint>

#include <archive_entry.h>
#include <linux/types.h>

namespace vfs::libarchive
{
class entry final
{
  public:
    entry() = delete;
    explicit entry(archive_entry* entry, const std::shared_ptr<archive>& archive) noexcept;

    [[nodiscard]] std::expected<void, std::error_code>
    extract(const std::filesystem::path& path) noexcept;

    [[nodiscard]] std::int64_t get_gid() const noexcept;
    [[nodiscard]] std::int64_t get_ino() const noexcept;
    [[nodiscard]] std::int64_t get_ino64() const noexcept;
    [[nodiscard]] std::int64_t get_size() const noexcept;
    [[nodiscard]] std::int64_t get_uid() const noexcept;
    [[nodiscard]] mode_t get_mode() const noexcept;
    [[nodiscard]] mode_t get_perm() const noexcept;
    [[nodiscard]] dev_t get_rdev() const noexcept;
    [[nodiscard]] dev_t get_rdevmajor() const noexcept;
    [[nodiscard]] dev_t get_rdevminor() const noexcept;
    [[nodiscard]] std::string get_hardlink() const noexcept;
    [[nodiscard]] std::string get_pathname() const noexcept;
    [[nodiscard]] std::string get_symlink() const noexcept;
    [[nodiscard]] std::string get_user_name() const noexcept;
    [[nodiscard]] std::string get_group_name() const noexcept;
    [[nodiscard]] std::uint32_t get_nlink() const noexcept;

  private:
    std::shared_ptr<archive_entry> entry_;
    std::shared_ptr<archive> archive_;
};
} // namespace vfs::libarchive
