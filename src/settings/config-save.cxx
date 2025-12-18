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
#include <format>

#include <glaze/glaze.hpp>

#include <ztd/extra/glaze.hxx>
#include <ztd/ztd.hxx>

#include "settings/config.hxx"
#include "settings/settings.hxx"

#include "logger.hxx"

[[nodiscard]] static config::settings
pack_settings(const std::shared_ptr<config::settings>& settings) noexcept
{
    config::settings s = *settings;

    return s;
}

void
config::save(const std::filesystem::path& path,
             const std::shared_ptr<config::settings>& settings) noexcept
{
    if (!std::filesystem::exists(path))
    {
        std::filesystem::create_directory(path);
    }

    const auto config_data =
        config_file_data{config::disk_format::version, pack_settings(settings)};

    std::string buffer;
    // TODO prettify=true segfaults when used in Gtk::Window destructor,
    // it was not doing it earlier need to investigate.
    // std::basic_string<char>::operator[](size_type): Assertion '__pos <= size()' failed.
    const auto ec =
        glz::write_file_json<glz::opts{.prettify = false}>(config_data,
                                                           (path / config::filename).c_str(),
                                                           buffer);

    logger::error_if(ec, "Failed to write config file: {}", glz::format_error(ec, buffer));
}
