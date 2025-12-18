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
#include <print>

#include <magic_enum/magic_enum.hpp>

#include <CLI/CLI.hpp>

#include "commandline/commandline.hxx"

#include "crash/crash.hxx"
#include "logger.hxx"

void
run_commandline(const commandline_opt_data_t& opt) noexcept
{
    if (opt->crash_list)
    {
        crash::list();
        std::exit(EXIT_SUCCESS);
    }

    if (opt->crash_recover)
    {
        crash::recover();
        std::exit(EXIT_SUCCESS);
    }

    if (opt->version)
    {
        std::println("{} {}", PACKAGE_NAME_FANCY, PACKAGE_VERSION);
        std::exit(EXIT_SUCCESS);
    }

    logger::initialize(opt->log_levels, opt->logfile);
}

void
setup_commandline(CLI::App& app, const commandline_opt_data_t& opt) noexcept
{
    app.add_flag("--crash-list", opt->crash_list, "List all crash files");
    app.add_flag("--crash-recover",
                 opt->crash_recover,
                 "Reopen archives using crash files (check with --crash-list first)");

    app.add_option("--loglevel", opt->raw_log_levels, "Set the loglevel. Format: domain=level")
        ->check(
            [&opt](const auto& value)
            {
                auto log_levels = magic_enum::enum_names<logger::detail::loglevel>();
                auto valid_domains = magic_enum::enum_names<logger::domain>();

                const auto pos = value.find('=');
                if (pos == std::string::npos)
                {
                    return std::string("Must be in format domain=level");
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

                opt->log_levels.insert({domain, level});

                return std::string();
            });

    app.add_option("--logfile", opt->logfile, "absolute path to the logfile")
        ->expected(1)
        ->check(
            [](const std::filesystem::path& input)
            {
                if (input.is_absolute())
                {
                    return std::string();
                }
                return std::format("Logfile path must be absolute: {}", input.string());
            });

    app.add_flag("-v,--version", opt->version, "Show version information");

    // Everything else
    app.add_option("files", opt->files, "[DIR | FILE | URL]...")->expected(0, -1);

    app.callback([opt]() { run_commandline(opt); });
}
