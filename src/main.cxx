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

#include <glibmm.h>
#include <gtkmm.h>

#include <CLI/CLI.hpp>

#include "commandline/commandline.hxx"

#include "gui/main-window.hxx"

int
main(int argc, char* argv[])
{
    CLI::App cli_app{PACKAGE_NAME_FANCY, "Manga/Comic Reader"};

    const auto opt = std::make_shared<commandline_opt_data>();
    setup_commandline(cli_app, opt);

    CLI11_PARSE(cli_app, argc, argv);

    Glib::set_prgname(PACKAGE_NAME);

    // command line is not handled by GTK
    auto app = Gtk::Application::create("org.thermitegod.mcomix");
    return app->make_window_and_run<gui::main_window>(0, nullptr, app, opt->files);
}
