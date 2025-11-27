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

#include <filesystem>

#include <cstdint>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include "gui/dialog/donate.hxx"

gui::dialog::donate::donate(Gtk::ApplicationWindow& parent)
{
    this->set_transient_for(parent);
    this->set_modal(true);

    this->set_size_request(500, 500);
    this->set_resizable(false);

    this->set_title("Support Dialog");

    // Content //

    this->box_ = Gtk::Box(Gtk::Orientation::VERTICAL, 5);
    this->box_.append(this->notebook_);

    auto key_controller = Gtk::EventControllerKey::create();
    key_controller->signal_key_pressed().connect(sigc::mem_fun(*this, &donate::on_key_press),
                                                 false);
    this->add_controller(key_controller);

    // BTC //

    std::filesystem::path btc_img = std::format("{}/{}", PACKAGE_IMAGES, "btc.png");
    if (!std::filesystem::exists(btc_img))
    { // Could not find image in system path, use image in repo.
        btc_img = std::format("{}/{}", PACKAGE_IMAGES_LOCAL, "btc.png");
    }

    this->btc_img_ = Gtk::Picture(btc_img.string());
    this->btc_img_.set_hexpand(true);
    this->btc_img_.set_vexpand(true);

    this->btc_label_.set_markup("<big>bc1qzus6vvyzvgqjxw8mxnj65fapjrmwuzvtlmpw72</big>");
    this->btc_label_.set_selectable(true);
    this->btc_label_.set_margin(5);

    this->btc_box_ = Gtk::Box(Gtk::Orientation::VERTICAL, 5);
    this->btc_box_.append(this->btc_img_);
    this->btc_box_.append(this->btc_label_);

    this->notebook_.append_page(this->btc_box_, "BTC");

    // ETH //

    std::filesystem::path eth_img = std::format("{}/{}", PACKAGE_IMAGES, "eth.png");
    if (!std::filesystem::exists(eth_img))
    { // Could not find image in system path, use image in repo.
        eth_img = std::format("{}/{}", PACKAGE_IMAGES_LOCAL, "eth.png");
    }

    this->eth_img_ = Gtk::Picture(eth_img.string());
    this->eth_img_.set_hexpand(true);
    this->eth_img_.set_vexpand(true);

    this->eth_label_.set_markup("<big>0x056d6eC68806Ab139C15B4Dd5736C45295AF0d32</big>");
    this->eth_label_.set_selectable(true);
    this->eth_label_.set_margin(5);

    this->eth_box_ = Gtk::Box(Gtk::Orientation::VERTICAL, 5);
    this->eth_box_.append(this->eth_img_);
    this->eth_box_.append(this->eth_label_);

    this->notebook_.append_page(this->eth_box_, "ETH");

    // Buttons //

    this->button_box_ = Gtk::Box(Gtk::Orientation::HORIZONTAL, 0);
    this->button_close_ = Gtk::Button("_Close", true);

    this->button_close_.signal_clicked().connect(
        sigc::mem_fun(*this, &donate::on_button_close_clicked));

    this->box_.append(this->button_box_);
    this->button_box_.set_halign(Gtk::Align::END);
    this->button_box_.append(this->button_close_);
    this->button_box_.set_margin(5);

    this->set_child(this->box_);

    this->present();
}

bool
gui::dialog::donate::on_key_press(std::uint32_t keyval, std::uint32_t keycode,
                                  Gdk::ModifierType state)
{
    (void)keycode;
    (void)state;
    if (keyval == GDK_KEY_Escape)
    {
        this->on_button_close_clicked();
    }
    return false;
}

void
gui::dialog::donate::on_button_close_clicked()
{
    this->close();
}
