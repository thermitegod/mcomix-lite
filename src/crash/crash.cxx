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

#include <chrono>
#include <filesystem>
#include <print>

#include <glibmm.h>

#include <glaze/glaze.hpp>

#include <ztd/ztd.hxx>

#include "vfs/user-dirs.hxx"

#include "crash/crash.hxx"
#include "logger.hxx"

void
crash::create(const std::filesystem::path& path, const std::filesystem::path& archive) noexcept
{
    auto data = crash_info{.path = archive, .opened = std::chrono::system_clock::now()};

    std::string buffer;
    const auto ec = glz::write_file_json(data, (path / "crash.json").c_str(), buffer);

    if (ec)
    {
        logger::error("Failed to write crash info: {}", glz::format_error(ec, buffer));
    }
}

void
crash::list() noexcept
{
    for (const auto& dfile : std::filesystem::directory_iterator(vfs::user::cache() / PACKAGE_NAME))
    {
        crash_info data;
        std::string buffer;
        const auto ec = glz::read_file_json(data, (dfile.path() / "crash.json").c_str(), buffer);

        if (ec)
        {
            logger::error("Failed to load crash file: {}", glz::format_error(ec, buffer));
            return;
        }

        std::println("{}", data.path.string());
    }
}

void
crash::recover() noexcept
{
    static auto quote = [](const std::filesystem::path& path) -> std::string
    { return std::format(R"("{}")", ztd::replace(path.string(), "\"", "\\\"")); };

    for (const auto& dfile : std::filesystem::directory_iterator(vfs::user::cache() / PACKAGE_NAME))
    {
        crash_info data;
        std::string buffer;
        const auto ec = glz::read_file_json(data, (dfile.path() / "crash.json").c_str(), buffer);

        if (ec)
        {
            logger::error("Failed to load crash file: {}", glz::format_error(ec, buffer));
            return;
        }

        std::println("Opening '{}'", data.path.string());
        Glib::spawn_command_line_async(std::format("{} {}", PACKAGE_NAME, quote(data.path)));
    }
}
