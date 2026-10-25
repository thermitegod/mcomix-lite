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
#include <memory>
#include <print>
#include <vector>

#include <cstdlib>

#include <giomm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include "gui/main-window.hxx"

#include "vfs/crash/crash.hxx"

#include "logger.hxx"

int
main(int argc, char* argv[])
{
    bool crash_list = false;
    bool crash_recover = false;
    bool version = false;
    std::vector<std::filesystem::path> files;

    try
    {
        Glib::OptionContext context("[FILES...]");
        context.set_summary("Manga/Comic Reader");

        Glib::OptionGroup group("main", PACKAGE_NAME_FANCY, "Application options");

        Glib::OptionEntry crash_list_entry;
        crash_list_entry.set_long_name("crash-list");
        crash_list_entry.set_description("List all crash files");
        group.add_entry(crash_list_entry, crash_list);

        Glib::OptionEntry crash_recover_entry;
        crash_recover_entry.set_long_name("crash-recover");
        crash_recover_entry.set_description("Reopen archives using crash files "
                                            "(check with --crash-list first)");
        group.add_entry(crash_recover_entry, crash_recover);

        Glib::OptionEntry version_entry;
        version_entry.set_long_name("version");
        version_entry.set_short_name('v');
        version_entry.set_description("Show version information");
        group.add_entry(version_entry, version);

        context.set_main_group(group);
        context.parse(argc, argv);

        files.reserve(static_cast<std::size_t>(argc - 1));
        for (const auto i : std::views::iota(1, argc))
        {
            const std::filesystem::path file{argv[i]};
            if (!std::filesystem::exists(file))
            {
                std::println(stderr, "CLI: file does not exist '{}'", file);
                continue;
            }
            files.emplace_back(file);
        }
    }
    catch (const Glib::Error& ex)
    {
        std::println(stderr, "Error parsing command-line options: {}", ex.what());
        return EXIT_FAILURE;
    }

    if (crash_list)
    {
        vfs::crash::list();
        return EXIT_SUCCESS;
    }

    if (crash_recover)
    {
        vfs::crash::recover();
        return EXIT_SUCCESS;
    }

    if (version)
    {
        std::println("{} {}", PACKAGE_NAME_FANCY, PACKAGE_VERSION);
        return EXIT_SUCCESS;
    }

    /////////////////////

    logger::initialize();

    auto app =
        Gtk::Application::create("org.thermitegod.webcomix", Gio::Application::Flags::NON_UNIQUE);

    auto settings = std::make_shared<config::settings>();
    config::manager config_manager(settings);
    config_manager.load();

    app->signal_activate().connect(
        [app, &files, settings]()
        {
            auto* window = Gtk::make_managed<gui::main_window>(app, files, settings);
            window->present();
        });

    const auto status = app->run();

    config_manager.save();

    return status;
}
