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

#include "gui/viewport.hxx"

#include "settings.hxx"

gui::viewport::viewport(const std::shared_ptr<config::settings>& settings) noexcept
    : settings_(settings)
{
    set_hexpand(true);
    set_vexpand(true);
    set_policy(Gtk::PolicyType::AUTOMATIC, Gtk::PolicyType::AUTOMATIC);

    box_.set_orientation(Gtk::Orientation::VERTICAL);
    box_.set_halign(Gtk::Align::CENTER);
    box_.set_valign(Gtk::Align::CENTER);
    box_.set_hexpand(false);
    box_.set_vexpand(false);

    set_child(box_);

    scroll_controller_ = Gtk::EventControllerScroll::create();
    scroll_controller_->set_flags(Gtk::EventControllerScroll::Flags::VERTICAL);
    scroll_controller_->signal_scroll().connect(sigc::mem_fun(*this, &gui::viewport::on_scroll),
                                                false);

    add_controller(scroll_controller_);
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
gui::viewport::set_picture_zoom(Gtk::Picture& picture,
                                const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept
{
#if 0
    // the default zoom detection causes all images
    // to get put into the scrolled windows allocated size.
    // do not want that so allow for overflow

    const bool is_default = is_default_zoom();

    picture.set_content_fit(Gtk::ContentFit::CONTAIN);

    if (is_default)
    {
        picture.set_size_request(-1, -1);
        picture.set_hexpand(true);
        picture.set_vexpand(true);
    }
    else
#endif
    {
        const auto orig_w = static_cast<std::double_t>(paintable->get_intrinsic_width());
        const auto orig_h = static_cast<std::double_t>(paintable->get_intrinsic_height());
        const auto target_w = static_cast<std::int32_t>(orig_w * zoom_);
        const auto target_h = static_cast<std::int32_t>(orig_h * zoom_);

        picture.set_hexpand(false);
        picture.set_vexpand(false);
        picture.set_size_request(target_w, target_h);
    }
}

void
gui::viewport::set_zoom(std::double_t zoom) noexcept
{
    zoom_ = zoom;

    std::size_t idx = 0;
    for (auto* child = box_.get_first_child(); child != nullptr; child = child->get_next_sibling())
    {
        if (auto* picture = dynamic_cast<Gtk::Picture*>(child))
        {
            if (idx < paintables_.size())
            {
                set_picture_zoom(*picture, paintables_[idx]);
            }
            ++idx;
        }
    }
}

std::double_t
gui::viewport::get_zoom() const noexcept
{
    return zoom_;
}

void
gui::viewport::add_picture(const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept
{
    paintables_.push_back(paintable);

    auto picture = Gtk::make_managed<Gtk::Picture>();

    picture->set_content_fit(Gtk::ContentFit::CONTAIN);
    picture->set_can_shrink(true);
    picture->set_halign(Gtk::Align::START);
    picture->set_valign(Gtk::Align::START);
    picture->set_hexpand(false);
    picture->set_vexpand(false);
    picture->set_paintable(paintable);
    picture->set_visible(true);

    set_picture_zoom(*picture, paintable);

    box_.append(*picture);
}

void
gui::viewport::hide_images() noexcept
{
    paintables_.clear();
    while (auto* child = box_.get_first_child())
    {
        box_.remove(*child);
    }
}
