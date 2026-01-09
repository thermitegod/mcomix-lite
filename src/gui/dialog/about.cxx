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

#include <vector>

#include <glibmm.h>
#include <gtkmm.h>

#include "gui/dialog/about.hxx"

gui::dialog::about::about(Gtk::ApplicationWindow& parent) noexcept
{
    this->set_transient_for(parent);
    this->set_modal(true);

    this->set_logo_icon_name("TODO"); // show the broken icon for now
    // TODO - need to make a logo
    // this->set_logo(Gdk::Texture::create_from_filename(""));

    this->set_program_name(PACKAGE_NAME_FANCY);
    this->set_version(PACKAGE_VERSION);
    this->set_comments("MComix is an image viewer specifically designed to handle manga, comics, "
                       "and image files.");
    this->set_copyright("Copyright (C) 2005-2026");
    this->set_license_type(Gtk::License::GPL_3_0);

    this->set_website(PACKAGE_GITHUB);
    this->set_website_label(PACKAGE_GITHUB);

    const std::vector<Glib::ustring> authors{
        "",
        "TODO",
        "",
        "Includes Code From:",
        "https://github.com/thermitegod/spacefm",
        "https://github.com/sourcefrog/natsort",
        "https://github.com/do-m-en/libarchive_cpp_wrapper",
    };
    this->set_authors(authors);

    const std::vector<Glib::ustring> artists = {
        "TODO",
    };
    this->set_artists(artists);

    this->present();
}
