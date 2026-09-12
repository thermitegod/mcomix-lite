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

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

namespace gui
{
class menubar : public Gtk::PopoverMenuBar
{
  public:
    explicit menubar() noexcept;

  private:
    [[nodiscard]] Glib::RefPtr<Gio::Menu> create_file() noexcept;
    [[nodiscard]] Glib::RefPtr<Gio::Menu> create_edit() noexcept;
    [[nodiscard]] Glib::RefPtr<Gio::Menu> create_view() noexcept;
    [[nodiscard]] Glib::RefPtr<Gio::Menu> create_navigation() noexcept;
    [[nodiscard]] Glib::RefPtr<Gio::Menu> create_bookmarks() noexcept;
    [[nodiscard]] Glib::RefPtr<Gio::Menu> create_tools() noexcept;
    [[nodiscard]] Glib::RefPtr<Gio::Menu> create_help() noexcept;
};
} // namespace gui
