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
#include <string>

#include <glaze/glaze.hpp>

#include <ztd/extra/glaze.hxx>
#include <ztd/ztd.hxx>

#include "settings/config.hxx"
#include "settings/settings.hxx"

#include "logger.hxx"

config::manager::manager(const std::shared_ptr<config::settings>& settings) : settings_(settings) {}

static void
parse_settings(const u64 version, const config::settings& loaded,
               const std::shared_ptr<config::settings>& settings) noexcept
{
    (void)version;

    *settings = loaded;
}

void
config::manager::load() noexcept
{
    if (!std::filesystem::exists(file_))
    {
        return;
    }

    config_file_format config_data{};
    std::string buffer;
    const auto ec = glz::read_file_json<glz::opts{.error_on_unknown_keys = false}>(config_data,
                                                                                   file_.c_str(),
                                                                                   buffer);

    if (ec)
    {
        // logger::error("Failed to load config file: {}", glz::format_error(ec, buffer));

        signal_load_error().emit(glz::format_error(ec, buffer));
        return;
    }

    parse_settings(config_data.version, config_data.settings, settings_);
}

[[nodiscard]] static config::settings
pack_settings(const std::shared_ptr<config::settings>& settings) noexcept
{
    config::settings s = *settings;

    return s;
}

void
config::manager::save() noexcept
{
    if (!std::filesystem::exists(file_.parent_path()))
    {
        std::filesystem::create_directories(file_.parent_path());
    }

    const auto config_data = config_file_format{version_, pack_settings(settings_)};

    std::string buffer;
    const auto ec =
        glz::write_file_json<glz::opts{.prettify = true}>(config_data, file_.c_str(), buffer);

    if (ec)
    {
        logger::error("Failed to write config file: {}", glz::format_error(ec, buffer));

        signal_save_error().emit(glz::format_error(ec, buffer));
    }
}
