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
#include <string>
#include <string_view>
#include <type_traits>

#include <sigc++/sigc++.h>

#include <glaze/json.hpp>

#include "vfs/user-dirs.hxx"

#include "logger.hxx"
#include "ztd/extra/glaze.hxx"
#include "ztd/ztd.hxx"

namespace config
{
struct state_t final
{
    bool maximized{false};
    std::int32_t width{800};
    std::int32_t height{600};
};

class state_manager final
{
  public:
    explicit state_manager(state_t& state, std::string_view package_name)
        : state_(state), file_(vfs::program::config() / std::format("{}_state.json", package_name))
    {
    }

    void
    load() noexcept
    {
        if (!std::filesystem::exists(file_))
        {
            return;
        }

        std::string buffer;
        const auto ec =
            glz::read_file_json<glz::opts{.error_on_unknown_keys = false}>(state_,
                                                                           file_.c_str(),
                                                                           buffer);

        if (ec)
        {
            logger::error("Failed to load state file: {}", glz::format_error(ec, buffer));
            signal_load_error_.emit(glz::format_error(ec, buffer));
        }
    }

    void
    save() noexcept
    {
        if (!std::filesystem::exists(file_.parent_path()))
        {
            std::error_code ec;
            std::filesystem::create_directories(file_.parent_path(), ec);
        }

        std::string buffer;
        const auto ec =
            glz::write_file_json<glz::opts{.prettify = true}>(state_, file_.c_str(), buffer);

        if (ec)
        {
            logger::error("Failed to write state file: {}", glz::format_error(ec, buffer));
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
    state_t& state_;
    std::filesystem::path file_;

    sigc::signal<void(std::string)> signal_load_error_;
    sigc::signal<void(std::string)> signal_save_error_;
};
} // namespace config
