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
                                    const std::shared_ptr<vfs::file_handler>& file_handler)
    : file_handler_(file_handler)
{
    const auto image_handler = this->file_handler_->image_handler();

    this->set_transient_for(parent);
    this->set_modal(true);

    this->set_size_request(560, 820);
    this->set_resizable(false);

    this->set_title("Page Select");

    auto key_controller = Gtk::EventControllerKey::create();
    key_controller->signal_key_pressed().connect(sigc::mem_fun(*this, &pageselect::on_key_press),
                                                 false);
    this->add_controller(key_controller);

    this->box_.set_orientation(Gtk::Orientation::VERTICAL);
    this->box_.set_margin(5);
    this->set_child(this->box_);

    auto adjust = Gtk::Adjustment::create(image_handler->get_current_page(),
                                          1,
                                          image_handler->get_number_of_pages());
    adjust->set_step_increment(1);
    adjust->set_page_increment(1);
    adjust->signal_value_changed().connect(
        [this, adjust]() { this->set_thumbnail(static_cast<std::int32_t>(adjust->get_value())); });

    this->image_box_.set_orientation(Gtk::Orientation::HORIZONTAL);
    this->image_box_.append(this->image_);
    this->image_.set_content_fit(Gtk::ContentFit::CONTAIN);
    this->image_.set_hexpand(true);
    this->image_.set_vexpand(true);
    this->image_.set_halign(Gtk::Align::CENTER);
    this->image_.set_valign(Gtk::Align::CENTER);
    this->scale_.set_orientation(Gtk::Orientation::VERTICAL);
    this->scale_.set_value(image_handler->get_current_page());
    this->scale_.set_draw_value(false);
    this->scale_.set_digits(0);
    this->scale_.set_adjustment(adjust);
    this->image_box_.append(this->scale_);
    this->box_.append(this->image_box_);

    this->spin_box_.set_orientation(Gtk::Orientation::HORIZONTAL);
    this->spin_.set_hexpand(true);
    this->spin_.set_value(image_handler->get_current_page());
    this->spin_.set_activates_default(true);
    this->spin_.set_numeric(true);
    this->spin_.set_adjustment(adjust);
    this->spin_box_.append(this->spin_);
    this->spin_label.set_text(std::format(" of {}", image_handler->get_number_of_pages()));
    this->spin_label.set_xalign(0.0);
    this->spin_label.set_yalign(0.5);
    this->spin_box_.set_margin_top(5);
    this->spin_box_.set_margin_bottom(5);
    this->spin_box_.append(this->spin_label);
    this->box_.append(this->spin_box_);

    this->button_box_ = Gtk::Box(Gtk::Orientation::HORIZONTAL, 5);
    this->button_cancel_ = Gtk::Button("Cancel", true);
    this->button_cancel_.set_focus_on_click(false);
    this->button_ok_ = Gtk::Button("Go", true);
    this->button_ok_.set_focus_on_click(false);
    this->button_box_.set_halign(Gtk::Align::END);
    this->button_box_.append(this->button_cancel_);
    this->button_box_.append(this->button_ok_);

    this->button_cancel_.signal_clicked().connect(
        sigc::mem_fun(*this, &pageselect::on_button_cancel_clicked));
    this->button_ok_.signal_clicked().connect(
        sigc::mem_fun(*this, &pageselect::on_button_ok_clicked));

    this->box_.append(this->button_box_);

    this->set_thumbnail(image_handler->get_current_page());

    this->set_visible(true);
}

void
gui::dialog::pageselect::on_button_cancel_clicked() noexcept
{
    this->close();
}

void
gui::dialog::pageselect::on_button_ok_clicked() noexcept
{
    this->signal_selected_page().emit(this->spin_.get_value_as_int());
    this->close();
}

bool
gui::dialog::pageselect::on_key_press(std::uint32_t keyval, std::uint32_t keycode,
                                      Gdk::ModifierType state)
{
    (void)keycode;
    (void)state;
    if (keyval == GDK_KEY_Return)
    {
        this->on_button_ok_clicked();
    }
    if (keyval == GDK_KEY_Escape)
    {
        this->on_button_cancel_clicked();
    }
    return false;
}

void
gui::dialog::pageselect::set_thumbnail(const page_t page) noexcept
{
    auto pixbuf = gui::lib::image_tools::create_thumbnail(
        this->file_handler_->image_handler()->image_files()->path_from_page(page),
        800);

    this->image_.set_pixbuf(pixbuf);
}
