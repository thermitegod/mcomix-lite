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
#include <flat_map>
#include <memory>
#include <vector>

#include <CLI/CLI.hpp>

struct commandline_opt_data : public std::enable_shared_from_this<commandline_opt_data>
{
    std::vector<std::filesystem::path> files;

    std::vector<std::string> raw_log_levels;
    std::flat_map<std::string, std::string> log_levels;
    // std::filesystem::path logfile{"/tmp/test.log"};
    std::filesystem::path logfile;

    bool version{false};
};

using commandline_opt_data_t = std::shared_ptr<commandline_opt_data>;

void setup_commandline(CLI::App& app, const commandline_opt_data_t& opt) noexcept;
