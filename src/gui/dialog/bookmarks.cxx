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

#include <chrono>

#include <glibmm.h>
#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include <ztd/ztd.hxx>

#include "gui/dialog/bookmarks.hxx"

gui::dialog::bookmarks::bookmarks(Gtk::ApplicationWindow& parent,
                                  const std::shared_ptr<vfs::file_handler>& file_handler,
                                  const std::shared_ptr<vfs::bookmarks>& bookmarks,
                                  const std::shared_ptr<config::settings>& settings) noexcept
    : file_handler_(file_handler), bookmarks_(bookmarks), settings_(settings)
{
    this->set_transient_for(parent);
    this->set_modal(true);

    this->set_size_request(800, 800);
    this->set_title("Bookmark Manager");
    this->set_resizable(false);

    // Content //

    this->box_ = Gtk::Box(Gtk::Orientation::VERTICAL, 5);
    this->box_.set_margin(5);
    this->set_child(this->box_);

    this->scrolled_window_.set_has_frame(true);
    this->scrolled_window_.set_policy(Gtk::PolicyType::NEVER, Gtk::PolicyType::AUTOMATIC);
    this->scrolled_window_.set_expand(true);
    this->box_.append(this->scrolled_window_);

    this->create_model();

    this->selection_model_ = Gtk::SingleSelection::create(this->liststore_);
    this->selection_model_->set_autoselect(true);
    this->selection_model_->set_can_unselect(true);
    this->columnview_.set_model(this->selection_model_);
    this->columnview_.set_reorderable(false);
    // this->columnview_.set_single_click_activate(true);
    this->columnview_.add_css_class("data-table");
    this->columnview_.signal_activate().connect([this]([[maybe_unused]] auto i)
                                                { this->on_button_ok_clicked(); });
    this->add_columns();
    this->scrolled_window_.set_child(this->columnview_);

    // keybindings //

    auto key_controller = Gtk::EventControllerKey::create();
    key_controller->signal_key_pressed().connect(sigc::mem_fun(*this, &bookmarks::on_key_press),
                                                 false);
    this->add_controller(key_controller);

    // Buttons //

    this->button_box_ = Gtk::Box(Gtk::Orientation::HORIZONTAL, 5);
    this->button_ok_ = Gtk::Button("Open", true);
    this->button_ok_.signal_clicked().connect([this]() { this->on_button_ok_clicked(); });
    this->button_close_ = Gtk::Button("Close", true);
    this->button_close_.signal_clicked().connect([this]() { this->on_button_close_clicked(); });
    this->button_remove_ = Gtk::Button("Remove", true);
    this->button_remove_.signal_clicked().connect([this]() { this->on_button_remove_clicked(); });
    this->button_remove_all_ = Gtk::Button("Remove All", true);
    this->button_remove_all_.signal_clicked().connect([this]()
                                                      { this->on_button_remove_all_clicked(); });

    this->box_.append(this->button_box_);
    this->button_box_.set_halign(Gtk::Align::END);
    this->button_box_.append(this->button_remove_all_);
    this->button_box_.append(this->button_remove_);
    this->button_box_.append(this->button_close_);
    this->button_box_.append(this->button_ok_);

    this->set_child(this->box_);

    this->set_visible(true);
}

bool
gui::dialog::bookmarks::on_key_press(std::uint32_t keyval, std::uint32_t keycode,
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
gui::dialog::bookmarks::on_button_ok_clicked() noexcept
{
    if (auto selected =
            std::dynamic_pointer_cast<ModelColumns>(this->selection_model_->get_selected_item()))
    {
        this->file_handler_->open_file_init({selected->path_}, selected->current_page_);
    }

    this->close();
}

void
gui::dialog::bookmarks::on_button_remove_clicked() noexcept
{
    if (auto selected =
            std::dynamic_pointer_cast<ModelColumns>(this->selection_model_->get_selected_item()))
    {
        this->bookmarks_->remove(selected->path_);
        this->liststore_->remove(selection_model_->get_selected());
    }
}

void
gui::dialog::bookmarks::on_button_remove_all_clicked() noexcept
{
    auto dialog = Gtk::AlertDialog::create("Remove All Bookmarks?");
    dialog->set_detail(
        std::format("This will remove '{}' bookmarks", this->bookmarks_->get_bookmarks().size()));
    dialog->set_modal(true);
    dialog->set_buttons({"Cancel", "Confirm"});
    dialog->set_cancel_button(0);
    dialog->set_default_button(0);

    auto slot = [this, dialog](Glib::RefPtr<Gio::AsyncResult>& result)
    {
        try
        {
            const auto response = dialog->choose_finish(result);
            if (response == 1)
            { // Confirm Button
                this->bookmarks_->remove_all();
                this->liststore_->remove_all();
            }
        }
        catch (...)
        {
        }
    };
    dialog->choose(*this, slot);
}

void
gui::dialog::bookmarks::on_button_close_clicked() noexcept
{
    this->close();
}

void
gui::dialog::bookmarks::create_model() noexcept
{
    this->liststore_ = Gio::ListStore<ModelColumns>::create();

    for (const auto& data : this->bookmarks_->get_bookmarks())
    {
        this->liststore_add_item(this->settings_->bookmark_manager_fullpath ? data.path
                                                                            : data.path.filename(),
                                 data.current_page,
                                 data.total_pages,
                                 data.created);
    }
}

void
gui::dialog::bookmarks::liststore_add_item(
    const std::filesystem::path path, const std::int32_t current_page,
    const std::int32_t total_pages, const std::chrono::system_clock::time_point created) noexcept
{
    this->liststore_->append(ModelColumns::create(path, current_page, total_pages, created));
}

void
gui::dialog::bookmarks::add_columns() noexcept
{
    { // path
        auto factory = Gtk::SignalListItemFactory::create();
        factory->signal_setup().connect(
            sigc::bind(sigc::mem_fun(*this, &bookmarks::on_setup_label), Gtk::Align::START));
        factory->signal_bind().connect(sigc::mem_fun(*this, &bookmarks::on_bind_path));
        auto column = Gtk::ColumnViewColumn::create("Path", factory);
        column->set_expand(true);
        this->columnview_.append_column(column);
    }

    { // current page
        auto factory = Gtk::SignalListItemFactory::create();
        factory->signal_setup().connect(
            sigc::bind(sigc::mem_fun(*this, &bookmarks::on_setup_label), Gtk::Align::END));
        factory->signal_bind().connect(sigc::mem_fun(*this, &bookmarks::on_bind_current_page));
        auto column = Gtk::ColumnViewColumn::create("Current Page", factory);
        this->columnview_.append_column(column);
    }

    { // total pages
        auto factory = Gtk::SignalListItemFactory::create();
        factory->signal_setup().connect(
            sigc::bind(sigc::mem_fun(*this, &bookmarks::on_setup_label), Gtk::Align::END));
        factory->signal_bind().connect(sigc::mem_fun(*this, &bookmarks::on_bind_total_pages));
        auto column = Gtk::ColumnViewColumn::create("Total Pages", factory);
        this->columnview_.append_column(column);
    }

    { // file sizes
        auto factory = Gtk::SignalListItemFactory::create();
        factory->signal_setup().connect(
            sigc::bind(sigc::mem_fun(*this, &bookmarks::on_setup_label), Gtk::Align::END));
        factory->signal_bind().connect(sigc::mem_fun(*this, &bookmarks::on_bind_created));
        auto column = Gtk::ColumnViewColumn::create("Created", factory);
        this->columnview_.append_column(column);
    }
}

void
gui::dialog::bookmarks::on_setup_label(const Glib::RefPtr<Gtk::ListItem>& list_item,
                                       Gtk::Align halign) noexcept
{
    list_item->set_child(*Gtk::make_managed<Gtk::Label>("", halign));
}

void
gui::dialog::bookmarks::on_bind_path(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept
{
    auto col = std::dynamic_pointer_cast<ModelColumns>(list_item->get_item());
    if (!col)
    {
        return;
    }
    auto* label = dynamic_cast<Gtk::Label*>(list_item->get_child());
    if (!label)
    {
        return;
    }
    label->set_text(col->path_.string());
}

void
gui::dialog::bookmarks::on_bind_current_page(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept
{
    auto col = std::dynamic_pointer_cast<ModelColumns>(list_item->get_item());
    if (!col)
    {
        return;
    }
    auto* label = dynamic_cast<Gtk::Label*>(list_item->get_child());
    if (!label)
    {
        return;
    }
    label->set_text(std::format("{}", col->current_page_));
}

void
gui::dialog::bookmarks::on_bind_total_pages(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept
{
    auto col = std::dynamic_pointer_cast<ModelColumns>(list_item->get_item());
    if (!col)
    {
        return;
    }
    auto* label = dynamic_cast<Gtk::Label*>(list_item->get_child());
    if (!label)
    {
        return;
    }
    label->set_text(std::format("{}", col->total_pages_));
}

void
gui::dialog::bookmarks::on_bind_created(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept
{
    auto col = std::dynamic_pointer_cast<ModelColumns>(list_item->get_item());
    if (!col)
    {
        return;
    }
    auto* label = dynamic_cast<Gtk::Label*>(list_item->get_child());
    if (!label)
    {
        return;
    }
    label->set_text(std::format("{}", std::chrono::floor<std::chrono::seconds>(col->created_)));
}
