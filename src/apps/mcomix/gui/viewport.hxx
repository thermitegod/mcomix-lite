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

#include <memory>
#include <span>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include "settings/settings.hxx"

namespace gui
{
class viewport : public Gtk::Box
{
  public:
    explicit viewport(const std::shared_ptr<config::settings>& settings) noexcept;

    void set(const std::span<Glib::RefPtr<Gdk::Paintable>>& paintables) noexcept;

    void hide_images() noexcept;
    void toggle_page_padding() noexcept;

  private:
    void set_left(const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept;
    void set_right(const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept;

    // Need to use two boxes to get images to stay connected
    Gtk::Box image_box_;
    Gtk::Picture image_left_;
    Gtk::Picture image_right_;

    std::shared_ptr<config::settings> settings_;
};
} // namespace gui
