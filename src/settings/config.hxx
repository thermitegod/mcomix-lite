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

#include <ztd/ztd.hxx>

#include "settings/settings.hxx"

#include "vfs/user-dirs.hxx"

namespace config
{
struct config_file_format final
{
    u64 version{version};
    config::settings settings;
};

class manager
{
  public:
    manager(const std::shared_ptr<config::settings>& settings);
    void load() noexcept;
    void save() noexcept;

  private:
    std::shared_ptr<config::settings> settings_;
    std::filesystem::path file_ = vfs::program::config() / "config.json";
    u64 version_ = 1_u64; // 1.0.0

  public:
    [[nodiscard]] auto
    signal_load_error() noexcept
    {
        return this->signal_load_error_;
    }

    [[nodiscard]] auto
    signal_save_error() noexcept
    {
        return this->signal_save_error_;
    }

  private:
    sigc::signal<void(std::string)> signal_load_error_;
    sigc::signal<void(std::string)> signal_save_error_;
};
} // namespace config
