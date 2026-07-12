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

#include "settings/settings.hxx"

#include "gui/viewport.hxx"

gui::viewport::viewport(const std::shared_ptr<config::settings>& settings) noexcept
    : settings_(settings)
{
    set_orientation(Gtk::Orientation::HORIZONTAL);
    set_halign(Gtk::Align::CENTER);
    set_valign(Gtk::Align::CENTER);
    set_hexpand(true);
    set_vexpand(true);

    image_box_.set_halign(Gtk::Align::CENTER);
    image_box_.set_valign(Gtk::Align::CENTER);
    image_box_.set_hexpand(false);
    image_box_.set_vexpand(false);

    image_left_.set_content_fit(Gtk::ContentFit::CONTAIN);
    image_left_.set_hexpand(true);
    image_left_.set_vexpand(true);
    image_left_.set_halign(Gtk::Align::CENTER);
    image_left_.set_valign(Gtk::Align::CENTER);

    if (settings_->double_page_center_space)
    {
        image_box_.set_spacing(2);
    }

    image_right_.set_content_fit(Gtk::ContentFit::CONTAIN);
    image_right_.set_hexpand(true);
    image_right_.set_vexpand(true);
    image_right_.set_halign(Gtk::Align::CENTER);
    image_right_.set_valign(Gtk::Align::CENTER);

    image_box_.append(image_left_);
    image_box_.append(image_right_);

    append(image_box_);

    property_orientation().signal_changed().connect(
        [this]() { image_box_.set_orientation(get_orientation()); });
}

void
gui::viewport::set(const std::span<Glib::RefPtr<Gdk::Paintable>>& paintables) noexcept
{
    assert(paintables.size() == 1 || paintables.size() == 2);

    if (paintables.size() == 1)
    {
        set_left(paintables[0]);
    }
    else if (paintables.size() == 2)
    {
        set_left(paintables[0]);
        set_right(paintables[1]);
    }
    else
    {
        std::unreachable();
    }
}

void
gui::viewport::set_left(const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept
{
    image_left_.set_paintable(paintable);
    image_left_.set_visible(true);
}

void
gui::viewport::set_right(const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept
{
    image_right_.set_paintable(paintable);
    image_right_.set_visible(true);
}

void
gui::viewport::toggle_page_padding() noexcept
{
    settings_->double_page_center_space = !settings_->double_page_center_space;
    if (image_box_.get_spacing() != 0)
    {
        image_box_.set_spacing(0);
    }
    else
    {
        image_box_.set_spacing(2);
    }
}

void
gui::viewport::hide_images() noexcept
{
    image_left_.set_paintable(nullptr);
    image_right_.set_paintable(nullptr);

    // hides old images before showing new ones
    // also if in double page mode and only a single
    // image is going to be shown, prevents a ghost second image
    image_left_.set_visible(false);
    image_right_.set_visible(false);
}
