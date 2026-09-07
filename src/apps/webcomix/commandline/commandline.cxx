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

#include <algorithm>
#include <filesystem>
#include <flat_map>
#include <optional>
#include <print>
#include <vector>

#include <cstdint>

#include <magic_enum/magic_enum.hpp>

#include <CLI/CLI.hpp>

#include <ztd/ztd.hxx>

#include "commandline/commandline.hxx"

#include "vfs/crash/crash.hxx"

#include "logger.hxx"

struct opts_data final
{
    std::vector<std::filesystem::path> files;

    std::vector<std::string> raw_log_levels;
    std::flat_map<std::string, std::string> log_levels;
    // std::filesystem::path logfile{"/tmp/test.log"};
    std::filesystem::path logfile;

    bool crash_list{false};
    bool crash_recover{false};

    bool build_debug{false};
    bool version{false};
};

std::optional<commandline::opts>
commandline::run(int argc, char* argv[]) noexcept
{
    CLI::App app{PACKAGE_NAME_FANCY, "Webcomic Reader"};
    opts_data opt{};

    ////////////////////////////////////

    app.add_flag("--crash-list", opt.crash_list, "List all crash files");
    app.add_flag("--crash-recover",
                 opt.crash_recover,
                 "Reopen archives using crash files (check with --crash-list first)");

    app.add_option("--loglevel", opt.raw_log_levels, "Set the loglevel. Format: domain=level")
        ->check(
            [&opt](const std::string& value) -> std::string
            {
                constexpr auto log_levels = magic_enum::enum_names<logger::detail::loglevel>();
                constexpr auto valid_domains = magic_enum::enum_names<logger::domain>();

                const auto pos = value.find('=');
                if (pos == std::string::npos)
                {
                    return "Must be in format domain=level";
                }

                const auto domain = value.substr(0, pos);
                if (!std::ranges::contains(valid_domains, domain))
                {
                    return std::format("Invalid domain: {}", domain);
                }

                const auto level = value.substr(pos + 1);
                if (!std::ranges::contains(log_levels, level))
                {
                    return std::format("Invalid log level: {}", level);
                }

                opt.log_levels.insert({domain, level});

                return {};
            });

    app.add_option("--logfile", opt.logfile, "absolute path to the logfile")
        ->expected(1)
        ->check(
            [](const std::filesystem::path& input) -> std::string
            {
                if (input.is_absolute())
                {
                    return {};
                }
                return std::format("Logfile path must be absolute: {}", input.string());
            });

#if defined(DEV_MODE)
    app.add_flag("--build-debug", opt.build_debug, "Show build information");
#endif

    app.add_flag("-v,--version", opt.version, "Show version information");

    // Everything else
    app.add_option("files", opt.files, "[FILES]...")->expected(0, -1);

    ////////////////////////////////////

    try
    {
        app.parse(argc, argv);
    }
    catch (const CLI::CallForHelp& e)
    {
        std::println("{}", app.help());
        return std::nullopt;
    }
    catch (const CLI::ParseError& e)
    {
        return std::nullopt;
    }

    ////////////////////////////////////

    if (opt.crash_list)
    {
        vfs::crash::list();
        return std::nullopt;
    }

    if (opt.crash_recover)
    {
        vfs::crash::recover();
        return std::nullopt;
    }

    if (opt.version)
    {
        std::println("{} {}", PACKAGE_NAME_FANCY, PACKAGE_VERSION);
        return std::nullopt;
    }

#if defined(DEV_MODE)
    if (opt.build_debug)
    {
        std::println("PACKAGE_NAME          = {}", PACKAGE_NAME);
        std::println("PACKAGE_NAME_FANCY    = {}", PACKAGE_NAME_FANCY);
        std::println("PACKAGE_VERSION       = {}", PACKAGE_VERSION);
        std::println("PACKAGE_GITHUB        = {}", PACKAGE_GITHUB);
        std::println("PACKAGE_BUGREPORT     = {}", PACKAGE_BUGREPORT);
        std::println("PACKAGE_ONLINE_DOCS   = {}", PACKAGE_ONLINE_DOCS);
        std::println("PACKAGE_IMAGES        = {}", PACKAGE_IMAGES);
        std::println("PACKAGE_IMAGES_LOCAL  = {}", PACKAGE_IMAGES_LOCAL);
        return std::nullopt;
    }
#endif

    logger::initialize(opt.log_levels, opt.logfile);

    ////////////////////////////////////

    return commandline::opts{
        .files = std::move(opt.files),
    };
}
