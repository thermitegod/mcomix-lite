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
#include <fstream>
#include <iterator>
#include <memory>
#include <system_error>
#include <vector>

#include <archive.h>

#include "entry.hxx"

namespace vfs::libarchive
{
class reader
{
  public:
    reader() = delete;
    reader(reader&&) = default;
    reader& operator=(reader&&) noexcept = default;
    reader(const reader&) = delete;
    reader& operator=(const reader&) = delete;

    [[nodiscard]] static std::expected<reader, std::error_code>
    create(const std::filesystem::path& path) noexcept;
    class iterator
    {
      public:
        using reference = std::expected<std::shared_ptr<entry>, std::error_code>;

        iterator() = default;
        explicit iterator(reader* reader) noexcept : reader_(reader) {}

        reference operator*() const noexcept;
        iterator& operator++() noexcept;
        bool operator==(std::default_sentinel_t) const noexcept;

      private:
        reader* reader_ = nullptr;
    };

    iterator begin() noexcept;
    std::default_sentinel_t end() const noexcept;

  private:
    void next_entry() noexcept;

    std::shared_ptr<archive> archive_;

    class reader_context final
    {
      public:
        explicit reader_context(const std::filesystem::path& path,
                                const std::size_t buffer_size) noexcept
            : stream_(path, std::ios::binary), buffer_(buffer_size)
        {
        }

        std::ifstream stream_;
        std::vector<char> buffer_;
    };
    std::unique_ptr<reader_context> context_;

    std::expected<std::shared_ptr<entry>, std::error_code> current_entry_;
    bool is_finished_ = false;

    explicit reader(std::shared_ptr<archive> ar, std::unique_ptr<reader_context> ctx) noexcept;
};
} // namespace vfs::libarchive
