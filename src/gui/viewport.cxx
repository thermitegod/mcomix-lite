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
    this->set_orientation(Gtk::Orientation::HORIZONTAL);
    this->set_halign(Gtk::Align::CENTER);
    this->set_valign(Gtk::Align::CENTER);
    this->set_hexpand(true);
    this->set_vexpand(true);

    this->image_box_.set_halign(Gtk::Align::CENTER);
    this->image_box_.set_valign(Gtk::Align::CENTER);
    this->image_box_.set_hexpand(false);
    this->image_box_.set_vexpand(false);

    this->image_left_.set_content_fit(Gtk::ContentFit::CONTAIN);
    this->image_left_.set_hexpand(true);
    this->image_left_.set_vexpand(true);
    this->image_left_.set_halign(Gtk::Align::CENTER);
    this->image_left_.set_valign(Gtk::Align::CENTER);

    if (this->settings_->double_page_center_space)
    {
        this->image_box_.set_spacing(2);
    }

    this->image_right_.set_content_fit(Gtk::ContentFit::CONTAIN);
    this->image_right_.set_hexpand(true);
    this->image_right_.set_vexpand(true);
    this->image_right_.set_halign(Gtk::Align::CENTER);
    this->image_right_.set_valign(Gtk::Align::CENTER);

    this->image_box_.append(this->image_left_);
    this->image_box_.append(this->image_right_);

    this->append(this->image_box_);

    this->property_orientation().signal_changed().connect(
        [this]() { this->image_box_.set_orientation(this->get_orientation()); });
}

void
gui::viewport::set(const std::span<Glib::RefPtr<Gdk::Paintable>>& paintables) noexcept
{
    assert(paintables.size() == 1 || paintables.size() == 2);

    if (paintables.size() == 1)
    {
        this->set_left(paintables[0]);
    }
    else if (paintables.size() == 2)
    {
        this->set_left(paintables[0]);
        this->set_right(paintables[1]);
    }
    else
    {
        std::unreachable();
    }
}

void
gui::viewport::set_left(const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept
{
    this->image_left_.set_paintable(paintable);
    this->image_left_.set_visible(true);
}

void
gui::viewport::set_right(const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept
{
    this->image_right_.set_paintable(paintable);
    this->image_right_.set_visible(true);
}

void
gui::viewport::toggle_page_padding() noexcept
{
    this->settings_->double_page_center_space = !this->settings_->double_page_center_space;
    if (this->image_box_.get_spacing() != 0)
    {
        this->image_box_.set_spacing(0);
    }
    else
    {
        this->image_box_.set_spacing(2);
    }
}

void
gui::viewport::hide_images() noexcept
{
    this->image_left_.set_paintable(nullptr);
    this->image_right_.set_paintable(nullptr);

    // hides old images before showing new ones
    // also if in double page mode and only a single
    // image is going to be shown, prevents a ghost second image
    this->image_left_.set_visible(false);
    this->image_right_.set_visible(false);
}
