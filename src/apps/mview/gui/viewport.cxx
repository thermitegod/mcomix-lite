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

#include <memory>
#include <span>
#include <utility>

#include <cassert>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include "gui/viewport.hxx"

#include "settings.hxx"

gui::viewport::viewport(const std::shared_ptr<config::settings>& settings) noexcept
    : settings_(settings)
{
    set_orientation(Gtk::Orientation::HORIZONTAL);
    set_halign(Gtk::Align::CENTER);
    set_valign(Gtk::Align::CENTER);
    set_hexpand(true);
    set_vexpand(true);

    image_.set_content_fit(Gtk::ContentFit::CONTAIN);
    image_.set_hexpand(true);
    image_.set_vexpand(true);
    image_.set_halign(Gtk::Align::CENTER);
    image_.set_valign(Gtk::Align::CENTER);

    append(image_);
}

void
gui::viewport::set(Glib::RefPtr<Gdk::Paintable> paintable) noexcept
{
    image_.set_visible(true);
    image_.set_paintable(paintable);
}

void
gui::viewport::hide_images() noexcept
{
    image_.set_paintable(nullptr);
}
