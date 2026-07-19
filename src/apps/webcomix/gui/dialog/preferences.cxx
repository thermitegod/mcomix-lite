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

#include <string_view>
#include <utility>

#include <glibmm.h>
#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include "settings/settings.hxx"

#include "gui/dialog/preferences.hxx"

class PreferencePage : public Gtk::ScrolledWindow
{
  public:
    explicit PreferencePage() noexcept
    {
        box_.set_orientation(Gtk::Orientation::VERTICAL);
        box_.set_margin(6);
        box_.set_homogeneous(false);
        box_.set_vexpand(true);

        set_child(box_);
    }

    void
    add_section(const std::string_view header) noexcept
    {
        Gtk::Label label;
        label.set_markup(std::format("<b>{}</b>", header.data()));
        label.set_xalign(0.0f);
        box_.append(label);
    }

    void
    add_row(const std::string_view left_item_name, Gtk::Widget& right_item) noexcept
    {
        Gtk::Label left_item(left_item_name.data());

        Gtk::Box left_box;
        Gtk::Box right_box;
        new_split_vboxes(left_box, right_box);
        left_box.append(left_item);
        right_box.append(right_item);
    }

    void
    add_row(Gtk::Label& left_item, Gtk::Widget& right_item) noexcept
    {
        Gtk::Box left_box;
        Gtk::Box right_box;
        new_split_vboxes(left_box, right_box);
        left_box.append(left_item);
        right_box.append(right_item);
    }

    void
    add_row(Gtk::Widget& item) noexcept
    {
        box_.append(item);
    }

    void
    add_checkbox(const std::string_view label, bool& option) noexcept
    {
        auto* button = Gtk::make_managed<Gtk::CheckButton>(std::format("{}", label));
        button->set_active(option);
        button->set_focus_on_click(false);

        button->signal_toggled().connect([button, &option]() { option = button->get_active(); });

        add_row(*button);
    }

  private:
    void
    new_split_vboxes(Gtk::Box& left_box, Gtk::Box& right_box) noexcept
    {
        left_box.set_spacing(6);
        left_box.set_homogeneous(false);

        right_box.set_spacing(6);
        right_box.set_homogeneous(false);

        Gtk::Box hbox = Gtk::Box(Gtk::Orientation::HORIZONTAL, 12);
        hbox.append(left_box);
        hbox.append(right_box);

        box_.append(hbox);
    }

    Gtk::Box box_;
};

gui::dialog::preferences::preferences(Gtk::ApplicationWindow& parent,
                                      const std::shared_ptr<config::settings>& settings) noexcept
    : settings_(settings)
{
    set_transient_for(parent);
    set_modal(true);

    set_size_request(600, 600);
    set_title("Preferences");
    set_resizable(false);

    box_ = Gtk::Box(Gtk::Orientation::VERTICAL, 5);
    box_.set_margin(5);

    box_.append(notebook_);

    init_behaviour_tab();
    init_display_tab();
    init_statusbar_tab();
    init_advanced_tab();

    auto key_controller = Gtk::EventControllerKey::create();
    key_controller->signal_key_pressed().connect(
        sigc::mem_fun(*this, &gui::dialog::preferences::on_key_press),
        false);
    add_controller(key_controller);

    button_box_ = Gtk::Box(Gtk::Orientation::HORIZONTAL, 5);
    button_close_ = Gtk::Button("Close", true);
    button_close_.signal_clicked().connect([this]() { on_button_close_clicked(); });
    button_box_.set_halign(Gtk::Align::END);
    button_box_.append(button_close_);
    box_.append(button_box_);

    set_child(box_);

    set_visible(true);
}

bool
gui::dialog::preferences::on_key_press(std::uint32_t keyval, std::uint32_t keycode,
                                       Gdk::ModifierType state) noexcept
{
    (void)keycode;
    (void)state;
    if (keyval == GDK_KEY_Escape)
    {
        on_button_close_clicked();
    }
    return false;
}

void
gui::dialog::preferences::on_button_close_clicked() noexcept
{
    close();
}

void
gui::dialog::preferences::on_setup_item(const Glib::RefPtr<Gtk::ListItem>& item) noexcept
{
    auto* label = Gtk::make_managed<Gtk::Label>();
    item->set_child(*label);
}

void
gui::dialog::preferences::on_bind_item(const Glib::RefPtr<Gtk::ListItem>& item) noexcept
{
    if (auto* label = dynamic_cast<Gtk::Label*>(item->get_child()))
    {
        if (auto info = std::dynamic_pointer_cast<ListColumns>(item->get_item()))
        {
            label->set_label(info->entry_);
        }
    }
}

void
gui::dialog::preferences::init_behaviour_tab() noexcept
{
    auto page = PreferencePage();

    page.add_section("Page Selection");

    {
        auto& opt = settings_->page_ff_step;

        auto adjust = Gtk::Adjustment::create(opt, 1, 100);
        adjust->set_step_increment(1);
        adjust->set_page_increment(1);
        adjust->signal_value_changed().connect(
            [&opt, adjust]() { opt = static_cast<std::int32_t>(adjust->get_value()); });

        auto button = Gtk::make_managed<Gtk::SpinButton>();
        button->set_value(opt);
        button->set_adjustment(adjust);

        page.add_row("Pages to change when fast forwarding", *button);
    }

    page.add_section("Navigation");

    page.add_checkbox("Prompt before auto changing archive", settings_->confirm_archive_change);

    auto tab_label = Gtk::Label("Behaviour");
    notebook_.append_page(page, tab_label);
}

void
gui::dialog::preferences::init_display_tab() noexcept
{
    auto page = PreferencePage();

    page.add_section("Thumbnails");

    {
        auto& opt = settings_->thumbnail_size;

        auto adjust = Gtk::Adjustment::create(opt, 50, 500);
        adjust->set_step_increment(1);
        adjust->set_page_increment(10);
        adjust->signal_value_changed().connect(
            [&opt, adjust]() { opt = static_cast<std::int32_t>(adjust->get_value()); });

        auto button = Gtk::make_managed<Gtk::SpinButton>();
        button->set_value(opt);
        button->set_adjustment(adjust);

        page.add_row("Thumbnail size (pixels)", *button);
    }

    page.add_section("Bookmark Manager");

    page.add_checkbox("Show full bookmark path", settings_->bookmark_manager_fullpath);

    page.add_section("General");

    page.add_checkbox("Always hide menubar", settings_->hide_menubar);
    page.add_checkbox("Always hide statusbar", settings_->hide_statusbar);

    page.add_section("Fullscreen");

    page.add_checkbox("Hide menubar when fullscreen", settings_->fullscreen.hide_menubar);
    page.add_checkbox("Hide statusbar when fullscreen", settings_->fullscreen.hide_statusbar);

    auto tab_label = Gtk::Label("Display");
    notebook_.append_page(page, tab_label);
}

void
gui::dialog::preferences::init_statusbar_tab() noexcept
{
    auto page = PreferencePage();

    page.add_section("Statusbar Fields");

    page.add_checkbox("Show page numbers", settings_->statusbar.page_numbers);
    page.add_checkbox("Show file numbers", settings_->statusbar.file_numbers);
    page.add_checkbox("Show archive filename", settings_->statusbar.archive_filename);
    page.add_checkbox("Show archive filesize", settings_->statusbar.archive_filesize);

    page.add_section("Statusbar Field Modifiers");

    page.add_checkbox("Show full path of current file",
                      settings_->statusbar.archive_filename_fullpath);

    auto tab_label = Gtk::Label("Statusbar");
    notebook_.append_page(page, tab_label);
}

void
gui::dialog::preferences::init_advanced_tab() noexcept
{
    auto page = PreferencePage();

    page.add_section("Moving Files");

    {
        const auto current = settings_->move_file;
        auto& opt = settings_->move_file;

        auto entry = Gtk::make_managed<Gtk::Entry>();
        entry->set_text(current);
        entry->set_hexpand(true);
        entry->signal_changed().connect([entry, &opt]() { opt = entry->get_text(); });

        page.add_row("Move file location (relative)", *entry);
    }

    page.add_checkbox("Use SI units", settings_->si_units);

    auto tab_label = Gtk::Label("Advanced");
    notebook_.append_page(page, tab_label);
}
