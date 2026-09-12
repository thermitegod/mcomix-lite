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

#include <concepts>
#include <filesystem>
#include <format>
#include <memory>
#include <string>
#include <string_view>
#include <type_traits>

#include <sigc++/sigc++.h>

#include <glaze/json.hpp>

#include "vfs/user-dirs.hxx"

#include "extra/glaze.hxx"
#include "logger.hxx"
#include "property.hxx"
#include "ztd/extra/glaze.hxx"
#include "ztd/ztd.hxx"

namespace config
{
template<typename T> struct config_file_format final
{
    u64 version{1_u64};
    T settings{};
};

template<typename T>
    requires std::is_class_v<T>
class manager
{
  public:
    explicit manager(const std::shared_ptr<T>& settings, std::string_view package_name)
        : settings_(settings), file_(vfs::program::config() / std::format("{}.json", package_name))
    {
    }

    void
    load() noexcept
    {
        if (!std::filesystem::exists(file_))
        {
            return;
        }

        config_file_format<T> config_data{};
        std::string buffer;
        const auto ec =
            glz::read_file_json<glz::opts{.error_on_unknown_keys = false}>(config_data,
                                                                           file_.c_str(),
                                                                           buffer);

        if (ec)
        {
            logger::error("Failed to load config file: {}", glz::format_error(ec, buffer));
            signal_load_error_.emit(glz::format_error(ec, buffer));
            return;
        }

        parse_settings(config_data.version, config_data.settings, settings_);
    }

    void
    save() noexcept
    {
        if (!std::filesystem::exists(file_.parent_path()))
        {
            std::error_code ec;
            std::filesystem::create_directories(file_.parent_path(), ec);
        }

        const auto config_data = config_file_format<T>{version_, pack_settings(settings_)};

        std::string buffer;
        const auto ec =
            glz::write_file_json<glz::opts{.prettify = true}>(config_data, file_.c_str(), buffer);

        if (ec)
        {
            logger::error("Failed to write config file: {}", glz::format_error(ec, buffer));
            signal_save_error_.emit(glz::format_error(ec, buffer));
        }
    }

    [[nodiscard]] auto
    signal_load_error() noexcept
    {
        return signal_load_error_;
    }

    [[nodiscard]] auto
    signal_save_error() noexcept
    {
        return signal_save_error_;
    }

  private:
    static void
    parse_settings(const u64 version, const T& loaded, const std::shared_ptr<T>& settings) noexcept
    {
        (void)version;
        if (settings)
        {
            *settings = loaded;
        }
    }

    [[nodiscard]] static T
    pack_settings(const std::shared_ptr<T>& settings) noexcept
    {
        return settings ? *settings : T{};
    }

    std::shared_ptr<T> settings_;
    std::filesystem::path file_;
    u64 version_ = 1_u64; // 1.0.0

    sigc::signal<void(std::string)> signal_load_error_;
    sigc::signal<void(std::string)> signal_save_error_;
};
} // namespace config
