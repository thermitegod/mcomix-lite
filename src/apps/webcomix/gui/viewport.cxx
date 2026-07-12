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

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include "settings/settings.hxx"

#include "gui/viewport.hxx"

gui::viewport::viewport(const std::shared_ptr<config::settings>& settings) noexcept
    : settings_(settings)
{
    box_.set_orientation(Gtk::Orientation::VERTICAL);
    box_.set_halign(Gtk::Align::CENTER);
    box_.set_valign(Gtk::Align::CENTER);
    box_.set_hexpand(true);
    box_.set_vexpand(true);

    set_child(box_);
}

void
gui::viewport::add_picture(const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept
{
    auto picture = Gtk::make_managed<Gtk::Picture>();

    picture->set_content_fit(Gtk::ContentFit::COVER);
    picture->set_hexpand(true);
    picture->set_vexpand(false);
    picture->set_halign(Gtk::Align::CENTER);
    picture->set_valign(Gtk::Align::START);
    picture->set_paintable(paintable);
    picture->set_visible(true);

    picture->set_can_shrink(false);

    box_.append(*picture);
}

void
gui::viewport::hide_images() noexcept
{
    while (auto* child = box_.get_first_child())
    {
        box_.remove(*child);
    }
}
