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

#include "settings.hxx"

namespace gui
{
class viewport : public Gtk::ScrolledWindow
{
  public:
    explicit viewport(const std::shared_ptr<config::settings>& settings) noexcept;

    void add_picture(const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept;

    void hide_images() noexcept;

    void zoom_reset() noexcept;
    void zoom_in() noexcept;
    void zoom_out() noexcept;

    [[nodiscard]] std::double_t get_zoom() const noexcept;

  private:
    Gtk::Box box_{Gtk::Orientation::VERTICAL};

    std::vector<Glib::RefPtr<Gdk::Paintable>> paintables_;

    Glib::RefPtr<Gtk::EventControllerScroll> scroll_controller_;

    bool on_scroll(std::double_t dx, std::double_t dy) noexcept;
    void set_zoom(std::double_t zoom) noexcept;
    void set_picture_zoom(Gtk::Picture& picture,
                          const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept;
    bool is_default_zoom() const noexcept;
    std::double_t zoom_ = 1.0;
    static constexpr std::double_t ZOOM_MIN = 1.0;
    static constexpr std::double_t ZOOM_MAX = 10.0;
    static constexpr std::double_t ZOOM_STEP = 0.1;

    void on_drag_begin(std::double_t start_x, std::double_t start_y) noexcept;
    void on_drag_update(std::double_t offset_x, std::double_t offset_y) noexcept;
    Glib::RefPtr<Gtk::GestureDrag> drag_controller_;
    std::double_t drag_start_hadj_val_ = 0.0;
    std::double_t drag_start_vadj_val_ = 0.0;

    std::shared_ptr<config::settings> settings_;
};
} // namespace gui
