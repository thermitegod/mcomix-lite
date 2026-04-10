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

class PreferencePage : public Gtk::Box
{
  public:
    explicit PreferencePage() noexcept
    {
        set_orientation(Gtk::Orientation::VERTICAL);
        set_margin(6);
        set_homogeneous(false);
        set_vexpand(true);
    }

    void
    add_section(const std::string_view header) noexcept
    {
        Gtk::Label label;
        label.set_markup(std::format("<b>{}</b>", header.data()));
        label.set_xalign(0.0f);
        append(label);
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
        append(item);
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
        append(hbox);
    }
};

gui::dialog::preferences::preferences(Gtk::ApplicationWindow& parent,
                                      const std::shared_ptr<config::settings>& settings) noexcept
    : settings_(settings)
{
    set_transient_for(parent);
    set_modal(true);

    set_size_request(470, 400);
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
gui::dialog::preferences::setup_listitem(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept
{
    auto* label = Gtk::make_managed<Gtk::Label>();
    list_item->set_child(*label);
}

void
gui::dialog::preferences::bind_listitem(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept
{
    if (auto* label = dynamic_cast<Gtk::Label*>(list_item->get_child()))
    {
        if (auto info = std::dynamic_pointer_cast<ListColumns>(list_item->get_item()))
        {
            label->set_label(info->entry_);
        }
    }
}

void
gui::dialog::preferences::init_behaviour_tab() noexcept
{
    auto page = PreferencePage();

    page.add_section("Page orientation");

    {
        auto& opt = settings_->default_manga_mode;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Set page orientation for manga");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    page.add_section("Double Page Mode");

    {
        auto& opt = settings_->default_double_page;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show two pages at a time");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->double_step_in_double_page_mode;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Change two pages at a time");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->virtual_double_page_for_fitting_images;

        auto factory = Gtk::SignalListItemFactory::create();
        factory->signal_setup().connect(sigc::mem_fun(*this, &preferences::setup_listitem));
        factory->signal_bind().connect(sigc::mem_fun(*this, &preferences::bind_listitem));

        auto store = Gio::ListStore<ListColumns>::create();
        store->append(ListColumns::create("Never", config::double_page::never));
        store->append(ListColumns::create("Title pages only", config::double_page::as_one_title));
        store->append(ListColumns::create("Wide pages Only", config::double_page::as_one_wide));
        store->append(ListColumns::create("Title and wide pages", config::double_page::always));

        auto drop = Gtk::make_managed<Gtk::DropDown>();
        drop->set_model(store);
        drop->set_factory(factory);
        drop->set_selected(opt);

        drop->property_selected_item().signal_changed().connect(
            [&opt, drop]() { opt = static_cast<config::double_page>(drop->get_selected()); });

        page.add_row("When to only show a single page", *drop);
    }

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

    {
        auto& opt = settings_->confirm_archive_change;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Prompt before auto opening next/prev archive");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    auto tab_label = Gtk::Label("Behaviour");
    notebook_.append_page(page, tab_label);
}

void
gui::dialog::preferences::init_display_tab() noexcept
{
    auto page = PreferencePage();

    page.add_section("Image Layout");

    {
        auto& opt = settings_->double_page_center_space;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show a page break between pages");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    page.add_section("Image Rotation");

    {
        auto& opt = settings_->rotation;

        auto factory = Gtk::SignalListItemFactory::create();
        factory->signal_setup().connect(sigc::mem_fun(*this, &preferences::setup_listitem));
        factory->signal_bind().connect(sigc::mem_fun(*this, &preferences::bind_listitem));

        auto store = Gio::ListStore<ListColumns>::create();
        store->append(ListColumns::create("0°", 0));
        store->append(ListColumns::create("90°", 90));
        store->append(ListColumns::create("180°", 180));
        store->append(ListColumns::create("270°", 270));

        auto drop = Gtk::make_managed<Gtk::DropDown>();
        drop->set_model(store);
        drop->set_factory(factory);
        drop->set_selected(
            [opt]() -> std::uint32_t
            {
                if (opt == 0)
                {
                    return 0;
                }
                else if (opt == 90)
                {
                    return 1;
                }
                else if (opt == 180)
                {
                    return 2;
                }
                else if (opt == 270)
                {
                    return 3;
                }
                std::unreachable();
            }());

        drop->property_selected_item().signal_changed().connect(
            [&opt, drop]()
            {
                if (auto selected =
                        std::dynamic_pointer_cast<ListColumns>(drop->get_selected_item()))
                {
                    opt = static_cast<std::int32_t>(selected->value_);
                }
            });

        page.add_row("Page rotation", *drop);
    }

    {
        auto& opt = settings_->keep_transformation;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Keep rotation between page changes");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

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

    {
        auto& opt = settings_->bookmark_manager_fullpath;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show full bookmark path");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    page.add_section("General");

    {
        auto& opt = settings_->hide_thumbar;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Always hide thumbnail sidebar");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->hide_menubar;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Always hide menubar");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->hide_statusbar;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Always hide statusbar");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    page.add_section("Fullscreen");

    {
        auto& opt = settings_->fullscreen.hide_thumbar;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Hide thumbnail sidebar when fullscreen");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->fullscreen.hide_menubar;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Hide menubar when fullscreen");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->fullscreen.hide_statusbar;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Hide statusbar when fullscreen");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    auto tab_label = Gtk::Label("Display");
    notebook_.append_page(page, tab_label);
}

void
gui::dialog::preferences::init_statusbar_tab() noexcept
{
    auto page = PreferencePage();

    page.add_section("Statusbar Fields");

    {
        auto& opt = settings_->statusbar.page_numbers;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show page numbers");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->statusbar.file_numbers;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show file numbers");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->statusbar.page_resolution;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show page resolution");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->statusbar.archive_filename;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show archive filename");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->statusbar.page_filesize;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show page filesize");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->statusbar.archive_filesize;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show archive filesize");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->statusbar.view_mode;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show current view mode");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    page.add_section("Statusbar Field Modifiers");

    {
        auto& opt = settings_->statusbar.page_resolution_zoom_scale;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show page scaling percent");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    {
        auto& opt = settings_->statusbar.archive_filename_fullpath;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Show full path of current file");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    auto tab_label = Gtk::Label("Statusbar");
    notebook_.append_page(page, tab_label);
}

void
gui::dialog::preferences::init_advanced_tab() noexcept
{
    auto page = PreferencePage();

#if 0
    page.add_section("Page Cache");

    {
        auto& opt = settings_->cache_behind;

        auto adjust = Gtk::Adjustment::create(opt, 1, 100);
        adjust->set_step_increment(1);
        adjust->set_page_increment(1);
        adjust->signal_value_changed().connect(
            [&opt, adjust]() { opt = static_cast<std::int32_t>(adjust->get_value()); });

        auto button = Gtk::make_managed<Gtk::SpinButton>();
        button->set_value(opt);
        button->set_adjustment(adjust);

        page.add_row("Pages to cache behind", *button);
    }

    {
        auto& opt = settings_->cache_forward;

        auto adjust = Gtk::Adjustment::create(opt, 1, 100);
        adjust->set_step_increment(1);
        adjust->set_page_increment(1);
        adjust->signal_value_changed().connect(
            [&opt, adjust]() { opt = static_cast<std::int32_t>(adjust->get_value()); });

        auto button = Gtk::make_managed<Gtk::SpinButton>();
        button->set_value(opt);
        button->set_adjustment(adjust);

        page.add_row("Pages to cache ahead", *button);
    }
#endif

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

    {
        auto& opt = settings_->si_units;

        auto button = Gtk::make_managed<Gtk::CheckButton>();
        button->set_label("Use SI units");
        button->set_active(opt);
        button->signal_toggled().connect([&opt]() { opt = !opt; });

        page.add_row(*button);
    }

    auto tab_label = Gtk::Label("Advanced");
    notebook_.append_page(page, tab_label);
}
