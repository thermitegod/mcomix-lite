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
    set_hexpand(true);
    set_vexpand(true);

    set_policy(Gtk::PolicyType::AUTOMATIC, Gtk::PolicyType::AUTOMATIC);

    image_.set_content_fit(Gtk::ContentFit::CONTAIN);
    image_.set_can_shrink(true);
    image_.set_halign(Gtk::Align::CENTER);
    image_.set_valign(Gtk::Align::CENTER);
    image_.set_hexpand(true);
    image_.set_vexpand(true);

    set_child(image_);

    scroll_controller_ = Gtk::EventControllerScroll::create();
    scroll_controller_->set_flags(Gtk::EventControllerScroll::Flags::VERTICAL);
    scroll_controller_->signal_scroll().connect(sigc::mem_fun(*this, &gui::viewport::on_scroll),
                                                false);

    add_controller(scroll_controller_);

    drag_controller_ = Gtk::GestureDrag::create();
    drag_controller_->set_button(GDK_BUTTON_PRIMARY);
    drag_controller_->signal_drag_begin().connect(
        sigc::mem_fun(*this, &gui::viewport::on_drag_begin));
    drag_controller_->signal_drag_update().connect(
        sigc::mem_fun(*this, &gui::viewport::on_drag_update));

    add_controller(drag_controller_);
}

bool
gui::viewport::on_scroll(std::double_t dx, std::double_t dy) noexcept
{
    (void)dx;

    const auto state = scroll_controller_->get_current_event_state();
    const auto ctrl_pressed =
        (state & Gdk::ModifierType::CONTROL_MASK) == Gdk::ModifierType::CONTROL_MASK;

    if (!ctrl_pressed)
    {
        return false;
    }

    if (dy < 0.0)
    {
        zoom_in();
    }
    else
    {
        zoom_out();
    }

    return true;
}

bool
gui::viewport::is_default_zoom() const noexcept
{
    return std::abs(zoom_ - 1.0) < 0.01;
}

void
gui::viewport::on_drag_begin(std::double_t start_x, std::double_t start_y) noexcept
{
    (void)start_x;
    (void)start_y;

    auto hadj = get_hadjustment();
    auto vadj = get_vadjustment();

    if (hadj)
    {
        drag_start_hadj_val_ = hadj->get_value();
    }
    if (vadj)
    {
        drag_start_vadj_val_ = vadj->get_value();
    }
}

void
gui::viewport::on_drag_update(std::double_t offset_x, std::double_t offset_y) noexcept
{
    auto hadj = get_hadjustment();
    auto vadj = get_vadjustment();

    if (hadj)
    {
        const std::double_t new_val = drag_start_hadj_val_ - offset_x;
        const std::double_t clamped_val =
            std::clamp(new_val, hadj->get_lower(), hadj->get_upper() - hadj->get_page_size());
        hadj->set_value(clamped_val);
    }

    if (vadj)
    {
        const std::double_t new_val = drag_start_vadj_val_ - offset_y;
        const std::double_t clamped_val =
            std::clamp(new_val, vadj->get_lower(), vadj->get_upper() - vadj->get_page_size());
        vadj->set_value(clamped_val);
    }
}

void
gui::viewport::zoom_reset() noexcept
{
    if (!is_default_zoom())
    {
        set_zoom(1.0);
    }
}

void
gui::viewport::zoom_in() noexcept
{
    set_zoom(std::clamp(zoom_ + ZOOM_STEP, ZOOM_MIN, ZOOM_MAX));
}

void
gui::viewport::zoom_out() noexcept
{
    set_zoom(std::clamp(zoom_ - ZOOM_STEP, ZOOM_MIN, ZOOM_MAX));
}

void
gui::viewport::set_zoom(std::double_t zoom) noexcept
{
    zoom_ = zoom;

    if (!paintable_)
    {
        return;
    }

    const bool is_default = is_default_zoom();

    image_.set_content_fit(Gtk::ContentFit::CONTAIN);

    if (is_default)
    {
        image_.set_size_request(-1, -1);
        image_.set_hexpand(true);
        image_.set_vexpand(true);
    }
    else
    {
        const auto orig_w = static_cast<std::double_t>(paintable_->get_intrinsic_width());
        const auto orig_h = static_cast<std::double_t>(paintable_->get_intrinsic_height());
        const auto target_w = static_cast<std::int32_t>(orig_w * zoom_);
        const auto target_h = static_cast<std::int32_t>(orig_h * zoom_);

        image_.set_hexpand(false);
        image_.set_vexpand(false);
        image_.set_size_request(target_w, target_h);
    }
}

std::double_t
gui::viewport::get_zoom() const noexcept
{
    return zoom_;
}

void
gui::viewport::set(Glib::RefPtr<Gdk::Paintable> paintable) noexcept
{
    paintable_ = paintable;
    image_.set_visible(true);
    image_.set_paintable(paintable);

    set_zoom(zoom_);
}

void
gui::viewport::hide_images() noexcept
{
    paintable_.reset();
    image_.set_paintable(nullptr);
}
