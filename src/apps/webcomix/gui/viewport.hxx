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
class viewport : public Gtk::ScrolledWindow
{
  public:
    explicit viewport(const std::shared_ptr<config::settings>& settings) noexcept;

    void add_picture(const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept;

    void hide_images() noexcept;

  private:
    Gtk::Box box_;

    std::shared_ptr<config::settings> settings_;
};
} // namespace gui
