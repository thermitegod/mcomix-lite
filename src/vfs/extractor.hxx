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

#include <sigc++/sigc++.h>

namespace vfs
{
class extractor
{
  public:
    extractor(const std::filesystem::path& archive);
    ~extractor();

    void list() noexcept;
    void extract() noexcept;

    [[nodiscard]] const std::filesystem::path path() const noexcept;

    void close() const noexcept;

    [[nodiscard]] auto
    signal_file_listed() noexcept
    {
        return this->signal_file_listed_;
    }

    [[nodiscard]] auto
    signal_file_extracted() noexcept
    {
        return this->signal_file_extracted_;
    }

  private:
    std::filesystem::path archive_;
    std::filesystem::path destination_;

    sigc::signal<void(std::vector<std::filesystem::path>)> signal_file_listed_;
    sigc::signal<void(std::filesystem::path)> signal_file_extracted_;
};
} // namespace vfs
