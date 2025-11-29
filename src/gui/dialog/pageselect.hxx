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

#include "vfs/file-handler.hxx"

#include "types.hxx"

namespace gui::dialog
{
class pageselect final : public Gtk::Window
{
  public:
    pageselect(Gtk::ApplicationWindow& parent,
               const std::shared_ptr<vfs::file_handler>& file_handler);

  private:
    Gtk::Box box_;

    Gtk::Picture image_;
    Gtk::Scale scale_;
    Gtk::Box image_box_;

    Gtk::SpinButton spin_;
    Gtk::Label spin_label;
    Gtk::Box spin_box_;

    Gtk::Button button_cancel_;
    Gtk::Button button_ok_;
    Gtk::Box button_box_;

    void on_button_cancel_clicked() noexcept;
    void on_button_ok_clicked() noexcept;

    bool on_key_press(std::uint32_t keyval, std::uint32_t keycode, Gdk::ModifierType state);

    void set_thumbnail(const page_t page) noexcept;

    std::shared_ptr<vfs::file_handler> file_handler_;

  public:
    [[nodiscard]] auto
    signal_selected_page() noexcept
    {
        return this->signal_selected_page_;
    }

  private:
    sigc::signal<void(std::int32_t)> signal_selected_page_;
};
} // namespace gui::dialog
