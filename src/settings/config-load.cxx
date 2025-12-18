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

static void
parse_settings(const u64 version, const config::settings& loaded,
               const std::shared_ptr<config::settings>& settings) noexcept
{
    (void)version;

    *settings = loaded;
}

void
config::load(const std::filesystem::path& path,
             const std::shared_ptr<config::settings>& settings) noexcept
{
    if (!std::filesystem::exists(path / config::filename))
    {
        return;
    }

    config_file_data config_data;
    std::string buffer;
    const auto ec = glz::read_file_json<glz::opts{.error_on_unknown_keys = false}>(
        config_data,
        (path / config::filename).c_str(),
        buffer);

    if (ec)
    {
        logger::error("Failed to load config file: {}", glz::format_error(ec, buffer));
        return;
    }

    parse_settings(config_data.version, config_data.settings, settings);
}
