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
#include <string_view>

#include <cstdint>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include "gui/dialog/donate.hxx"

#include "gui/lib/image-tools.hxx"

gui::dialog::donate::page::page() noexcept
{
    this->set_orientation(Gtk::Orientation::VERTICAL);
    this->set_spacing(5);

    this->img_.set_hexpand(true);
    this->img_.set_vexpand(true);

    this->label_.set_selectable(true);
    this->label_.set_margin(5);

    this->append(this->img_);
    this->append(this->label_);
}

void
gui::dialog::donate::page::set_image(const std::filesystem::path& path) noexcept
{
#if defined(PIXBUF_BACKEND)
    this->img_.set_pixbuf(gui::lib::image_tools::load_pixbuf(path));
#else
    this->img_.set_paintable(gui::lib::image_tools::load_texture(path));
#endif
}

void
gui::dialog::donate::page::set_label(const std::string_view text) noexcept
{
    this->label_.set_markup(std::format("<big>{}</big>", text));
}

gui::dialog::donate::donate(Gtk::ApplicationWindow& parent) noexcept
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

    { // BTC //
        auto img = std::filesystem::path(PACKAGE_IMAGES) / "btc.png";
        if (!std::filesystem::exists(img))
        { // Could not find image in system path, use image in repo.
            img = std::filesystem::path(PACKAGE_IMAGES_LOCAL) / "btc.png";
        }

        auto page = donate::page();
        page.set_image(img);
        page.set_label("bc1qzus6vvyzvgqjxw8mxnj65fapjrmwuzvtlmpw72");

        this->notebook_.append_page(page, "BTC");
    }

    { // ETH //
        auto img = std::filesystem::path(PACKAGE_IMAGES) / "eth.png";
        if (!std::filesystem::exists(img))
        { // Could not find image in system path, use image in repo.
            img = std::filesystem::path(PACKAGE_IMAGES_LOCAL) / "eth.png";
        }

        auto page = donate::page();
        page.set_image(img);
        page.set_label("0x056d6eC68806Ab139C15B4Dd5736C45295AF0d32");

        this->notebook_.append_page(page, "ETH");
    }

    // Buttons //

    this->button_box_ = Gtk::Box(Gtk::Orientation::HORIZONTAL, 0);
    this->button_close_ = Gtk::Button("_Close", true);
    this->button_close_.signal_clicked().connect([this]() { this->on_button_close_clicked(); });

    this->box_.append(this->button_box_);
    this->button_box_.set_halign(Gtk::Align::END);
    this->button_box_.append(this->button_close_);
    this->button_box_.set_margin(5);

    this->set_child(this->box_);

    this->present();
}

bool
gui::dialog::donate::on_key_press(std::uint32_t keyval, std::uint32_t keycode,
                                  Gdk::ModifierType state) noexcept
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
gui::dialog::donate::on_button_close_clicked() noexcept
{
    this->close();
}
