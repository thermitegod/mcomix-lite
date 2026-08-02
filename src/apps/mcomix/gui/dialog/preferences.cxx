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

#include <array>
#include <string_view>
#include <utility>

#include <glibmm.h>
#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include "settings/settings.hxx"

#include "gui/dialog/preferences.hxx"
#include "gui/dialog/widgets/button-box.hxx"

class preference_page : public Gtk::ScrolledWindow
{
  public:
    explicit preference_page() noexcept
    {
        box_.set_orientation(Gtk::Orientation::VERTICAL);
        box_.set_margin(6);
        box_.set_homogeneous(false);
        box_.set_vexpand(true);

        set_child(box_);
    }

    void
    add_section(std::string_view header) noexcept
    {
        auto* label = Gtk::make_managed<Gtk::Label>();
        label->set_markup(std::format("<b>{}</b>", header));
        label->set_xalign(0.0f);
        box_.append(*label);
    }

    void
    add_row(std::string_view left_item_name, Gtk::Widget& right_item) noexcept
    {
        auto* left_item = Gtk::make_managed<Gtk::Label>(std::string(left_item_name));

        auto [left_box, right_box] = create_split_vboxes();
        left_box->append(*left_item);
        right_box->append(right_item);
    }

    void
    add_row(Gtk::Widget& left_item, Gtk::Widget& right_item) noexcept
    {
        auto [left_box, right_box] = create_split_vboxes();
        left_box->append(left_item);
        right_box->append(right_item);
    }

    void
    add_row(Gtk::Widget& item) noexcept
    {
        box_.append(item);
    }

    void
    add_checkbox(std::string_view label, bool& option) noexcept
    {
        auto* button = Gtk::make_managed<Gtk::CheckButton>(std::string(label));
        button->set_active(option);
        button->set_focus_on_click(false);

        button->signal_toggled().connect([button, &option]() { option = button->get_active(); });

        add_row(*button);
    }

    void
    add_checkbox(std::string_view label, ::Property<bool>& option) noexcept
    {
        auto* button = Gtk::make_managed<Gtk::CheckButton>(std::string(label));
        button->set_active(option);
        button->set_focus_on_click(false);

        button->signal_toggled().connect([button, &option]() { option = button->get_active(); });

        add_row(*button);
    }

  private:
    std::array<Gtk::Box*, 2>
    create_split_vboxes() noexcept
    {
        auto* left_box = Gtk::make_managed<Gtk::Box>();
        left_box->set_spacing(6);
        left_box->set_homogeneous(false);

        auto* right_box = Gtk::make_managed<Gtk::Box>();
        right_box->set_spacing(6);
        right_box->set_homogeneous(false);

        auto* hbox = Gtk::make_managed<Gtk::Box>(Gtk::Orientation::HORIZONTAL, 12);
        hbox->append(*left_box);
        hbox->append(*right_box);

        box_.append(*hbox);

        return {left_box, right_box};
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

    // Buttons //
    auto* buttons = gui::widget::ButtonBox::create({
        {"Close", [this] { on_button_close_clicked(); }, &button_close_},
    });
    box_.append(*buttons);

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
    auto page = Gtk::make_managed<preference_page>();
    notebook_.append_page(*page, "Behaviour");

    page->add_section("Page orientation");

    page->add_checkbox("Set page orientation for manga", settings_->default_manga_mode);

    page->add_section("Double Page Mode");

    page->add_checkbox("Show two pages at a time", settings_->default_double_page);
    page->add_checkbox("Change two pages at a time", settings_->double_step_in_double_page_mode);

    {
        auto& opt = settings_->virtual_double_page_for_fitting_images;

        auto factory = Gtk::SignalListItemFactory::create();
        factory->signal_setup().connect(sigc::mem_fun(*this, &preferences::on_setup_item));
        factory->signal_bind().connect(sigc::mem_fun(*this, &preferences::on_bind_item));

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

        page->add_row("When to only show a single page", *drop);
    }

    page->add_section("Page Selection");

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

        page->add_row("Pages to change when fast forwarding", *button);
    }

    page->add_section("Navigation");

    page->add_checkbox("Prompt before auto changing archive", settings_->confirm_archive_change);
}

void
gui::dialog::preferences::init_display_tab() noexcept
{
    auto page = Gtk::make_managed<preference_page>();
    notebook_.append_page(*page, "Display");

    page->add_section("Image Layout");

    page->add_checkbox("Show a page break between pages", settings_->double_page_center_space);

    page->add_section("Image Rotation");

    {
        auto& opt = settings_->rotation;

        auto factory = Gtk::SignalListItemFactory::create();
        factory->signal_setup().connect(sigc::mem_fun(*this, &preferences::on_setup_item));
        factory->signal_bind().connect(sigc::mem_fun(*this, &preferences::on_bind_item));

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

        page->add_row("Page rotation", *drop);
    }

    page->add_checkbox("Keep rotation between page changes", settings_->keep_transformation);

    page->add_section("Thumbnails");

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

        page->add_row("Thumbnail size (pixels)", *button);
    }

    page->add_section("Bookmark Manager");

    page->add_checkbox("Show full bookmark path", settings_->bookmark_manager_fullpath);

    page->add_section("General");

    page->add_checkbox("Always hide thumbnail sidebar", settings_->hide_thumbar);
    page->add_checkbox("Always hide menubar", settings_->hide_menubar);
    page->add_checkbox("Always hide statusbar", settings_->hide_statusbar);

    page->add_section("Fullscreen");

    page->add_checkbox("Hide thumbnail sidebar when fullscreen",
                       settings_->fullscreen.hide_thumbar);
    page->add_checkbox("Hide menubar when fullscreen", settings_->fullscreen.hide_menubar);
    page->add_checkbox("Hide statusbar when fullscreen", settings_->fullscreen.hide_statusbar);
}

void
gui::dialog::preferences::init_statusbar_tab() noexcept
{
    auto page = Gtk::make_managed<preference_page>();
    notebook_.append_page(*page, "Statusbar");

    page->add_section("Statusbar Fields");

    page->add_checkbox("Show page numbers", settings_->statusbar.page_numbers);
    page->add_checkbox("Show file numbers", settings_->statusbar.file_numbers);
    page->add_checkbox("Show page resolution", settings_->statusbar.page_resolution);
    page->add_checkbox("Show archive filename", settings_->statusbar.archive_filename);
    page->add_checkbox("Show page filesize", settings_->statusbar.page_filesize);
    page->add_checkbox("Show archive filesize", settings_->statusbar.archive_filesize);
    page->add_checkbox("Show current view mode", settings_->statusbar.view_mode);

    page->add_section("Statusbar Field Modifiers");

    page->add_checkbox("Show page scaling percent",
                       settings_->statusbar.page_resolution_zoom_scale);
    page->add_checkbox("Show full path of current file",
                       settings_->statusbar.archive_filename_fullpath);
}

void
gui::dialog::preferences::init_advanced_tab() noexcept
{
    auto page = Gtk::make_managed<preference_page>();
    notebook_.append_page(*page, "Advanced");

    page->add_section("Moving Files");

    {
        const auto current = settings_->move_file;
        auto& opt = settings_->move_file;

        auto entry = Gtk::make_managed<Gtk::Entry>();
        entry->set_text(current);
        entry->set_hexpand(true);
        entry->signal_changed().connect([entry, &opt]() { opt = entry->get_text(); });

        page->add_row("Move file location (relative)", *entry);
    }

    page->add_checkbox("Use SI units", settings_->si_units);
}
