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

#include <ztd/ztd.hxx>

#include "settings/settings.hxx"

namespace config
{
struct config_file_data final
{
    u64 version;
    config::settings settings;
};

void load(const std::filesystem::path& path,
          const std::shared_ptr<config::settings>& settings) noexcept;
void save(const std::filesystem::path& path,
          const std::shared_ptr<config::settings>& settings) noexcept;

const std::filesystem::path filename{"config.json"};

namespace disk_format
{
constexpr u64 version = 1_u64; // 1.0.0
} // namespace disk_format
} // namespace config
