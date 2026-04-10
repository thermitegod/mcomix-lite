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

#include "gui/dialog/pageselect.hxx"

#include "gui/lib/image-tools.hxx"

#include "vfs/file-handler.hxx"

gui::dialog::pageselect::pageselect(Gtk::ApplicationWindow& parent,
                                    const std::shared_ptr<vfs::file_handler>& file_handler) noexcept
    : file_handler_(file_handler)
{
    const auto image_handler = file_handler_->image_handler();

    set_transient_for(parent);
    set_modal(true);

    set_size_request(560, 820);
    set_resizable(false);

    set_title("Page Select");

    auto key_controller = Gtk::EventControllerKey::create();
    key_controller->signal_key_pressed().connect(sigc::mem_fun(*this, &pageselect::on_key_press),
                                                 false);
    add_controller(key_controller);

    box_.set_orientation(Gtk::Orientation::VERTICAL);
    box_.set_margin(5);
    set_child(box_);

    auto adjust = Gtk::Adjustment::create(image_handler->get_current_page(),
                                          1,
                                          image_handler->get_number_of_pages());
    adjust->set_step_increment(1);
    adjust->set_page_increment(1);
    adjust->signal_value_changed().connect(
        [this, adjust]() { set_thumbnail(static_cast<std::int32_t>(adjust->get_value())); });

    image_box_.set_orientation(Gtk::Orientation::HORIZONTAL);
    image_box_.append(image_);
    image_.set_content_fit(Gtk::ContentFit::CONTAIN);
    image_.set_hexpand(true);
    image_.set_vexpand(true);
    image_.set_halign(Gtk::Align::CENTER);
    image_.set_valign(Gtk::Align::CENTER);
    scale_.set_orientation(Gtk::Orientation::VERTICAL);
    scale_.set_value(image_handler->get_current_page());
    scale_.set_draw_value(false);
    scale_.set_digits(0);
    scale_.set_adjustment(adjust);
    image_box_.append(scale_);
    box_.append(image_box_);

    spin_box_.set_orientation(Gtk::Orientation::HORIZONTAL);
    spin_.set_hexpand(true);
    spin_.set_value(image_handler->get_current_page());
    spin_.set_activates_default(true);
    spin_.set_numeric(true);
    spin_.set_adjustment(adjust);
    spin_box_.append(spin_);
    spin_label.set_text(std::format(" of {}", image_handler->get_number_of_pages()));
    spin_label.set_xalign(0.0);
    spin_label.set_yalign(0.5);
    spin_box_.set_margin_top(5);
    spin_box_.set_margin_bottom(5);
    spin_box_.append(spin_label);
    box_.append(spin_box_);

    button_box_ = Gtk::Box(Gtk::Orientation::HORIZONTAL, 5);
    button_cancel_ = Gtk::Button("Cancel", true);
    button_cancel_.set_focus_on_click(false);
    button_ok_ = Gtk::Button("Go", true);
    button_ok_.set_focus_on_click(false);
    button_box_.set_halign(Gtk::Align::END);
    button_box_.append(button_cancel_);
    button_box_.append(button_ok_);

    button_ok_.signal_clicked().connect([this]() { on_button_ok_clicked(); });
    button_cancel_.signal_clicked().connect([this]() { on_button_cancel_clicked(); });

    box_.append(button_box_);

    set_thumbnail(image_handler->get_current_page());

    set_visible(true);
}

void
gui::dialog::pageselect::on_button_cancel_clicked() noexcept
{
    close();
}

void
gui::dialog::pageselect::on_button_ok_clicked() noexcept
{
    signal_selected_page().emit(spin_.get_value_as_int());
    close();
}

bool
gui::dialog::pageselect::on_key_press(std::uint32_t keyval, std::uint32_t keycode,
                                      Gdk::ModifierType state)
{
    (void)keycode;
    (void)state;
    if (keyval == GDK_KEY_Return)
    {
        on_button_ok_clicked();
    }
    if (keyval == GDK_KEY_Escape)
    {
        on_button_cancel_clicked();
    }
    return false;
}

void
gui::dialog::pageselect::set_thumbnail(const page_t page) noexcept
{
    auto paintable = gui::lib::image_tools::create_thumbnail(
        file_handler_->image_handler()->get_path_to_page(page),
        800);

    image_.set_paintable(paintable);
}
