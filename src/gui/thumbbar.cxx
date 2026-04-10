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

#include <pthread.h>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include <ztd/ztd.hxx>

#include "settings/settings.hxx"

#include "gui/thumbbar.hxx"

// very helpful, used as the template for this widget.
// https://github.com/GNOME/gtkmm/blob/master/demos/gtk-demo/example_listview_applauncher.cc

gui::thumbbar::thumbbar(const std::shared_ptr<config::settings>& settings) noexcept
    : settings(settings)
{
    set_has_frame(true);
    set_policy(Gtk::PolicyType::NEVER, Gtk::PolicyType::AUTOMATIC);
    set_hexpand(false);
    set_vexpand(true);
    set_overlay_scrolling(false);
    set_focusable(false);

    scroll_info_ = Gtk::ScrollInfo::create();
    scroll_info_->set_enable_vertical(true);

    liststore_ = Gio::ListStore<ModelList>::create();

    selection_model_ = Gtk::SingleSelection::create(liststore_);
    selection_model_->set_autoselect(false);
    // selection_model_->set_selected(1);
    selection_model_->set_can_unselect(false);

    auto factory = Gtk::SignalListItemFactory::create();
    factory->signal_setup().connect(sigc::mem_fun(*this, &thumbbar::setup_listitem));
    factory->signal_bind().connect(sigc::mem_fun(*this, &thumbbar::bind_listitem));

    listview_ = Gtk::ListView(Gtk::SingleSelection::create(selection_model_), factory);
    listview_.set_single_click_activate(true);
    listview_.signal_activate().connect(sigc::mem_fun(*this, &thumbbar::activate));
    listview_.set_focusable(false);

    set_child(listview_);

    // thumbnail create thread
    thumbnailer_.signal_thumbnail_created().connect([this](const auto page, const auto& paintable)
                                                    { add_item(page, paintable); });

    thumbnailer_thread_ =
        std::jthread([this](const std::stop_token& stoken) { thumbnailer_.run(stoken); });
    pthread_setname_np(thumbnailer_thread_.native_handle(), "thumbnailer");
}

gui::thumbbar::~thumbbar() noexcept
{
    thumbnailer_thread_.request_stop();
    thumbnailer_thread_.join();
}

void
gui::thumbbar::request(const page_t page, const std::filesystem::path& filename) noexcept
{
    thumbnailer_.request({page, filename, settings->thumbnail_size});
}

void
gui::thumbbar::add_item(const page_t page, const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept
{
    Glib::signal_idle().connect_once([this, page, paintable]()
                                     { liststore_->append(ModelList::create(page, paintable)); });
}

void
gui::thumbbar::set_page(const page_t page) noexcept
{
    const auto position = static_cast<std::uint32_t>(page - 1);

    selection_model_->set_selected(position);

    auto item =
        std::dynamic_pointer_cast<Gio::ListModel>(listview_.get_model())->get_object(position);
    if (item)
    {
        listview_.scroll_to(position, Gtk::ListScrollFlags::SELECT, scroll_info_);
    }
}

void
gui::thumbbar::clear() noexcept
{
    // simply restarting the thumbnailer is the best way to
    // clear out the request queue. the queue is only a problem
    // when changing archives before all thumbnails have been loaded.
    thumbnailer_thread_.request_stop();
    thumbnailer_thread_.join();

    thumbnailer_thread_ =
        std::jthread([this](const std::stop_token& stoken) { thumbnailer_.run(stoken); });
    pthread_setname_np(thumbnailer_thread_.native_handle(), "thumbnailer");

    liststore_->remove_all();
}

void
gui::thumbbar::setup_listitem(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept
{
    auto box = Gtk::make_managed<Gtk::Box>(Gtk::Orientation::HORIZONTAL, 5);
    box->set_hexpand(false);
    box->set_vexpand(false);
    box->set_halign(Gtk::Align::CENTER);
    box->set_valign(Gtk::Align::CENTER);
    box->set_margin_end(20);

    auto label = Gtk::make_managed<Gtk::Label>();
    label->set_halign(Gtk::Align::START);
    label->set_valign(Gtk::Align::CENTER);
    box->append(*label);

    auto image = Gtk::make_managed<Gtk::Picture>();
    image->set_content_fit(Gtk::ContentFit::CONTAIN);
    image->set_hexpand(false);
    image->set_vexpand(false);
    image->set_halign(Gtk::Align::CENTER);
    image->set_valign(Gtk::Align::CENTER);
    image->set_can_shrink(false);
    box->append(*image);

    list_item->set_focusable(false);
    list_item->set_child(*box);
}

void
gui::thumbbar::bind_listitem(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept
{
    if (auto label = dynamic_cast<Gtk::Label*>(list_item->get_child()->get_first_child()))
    {
        if (auto image = dynamic_cast<Gtk::Picture*>(label->get_next_sibling()))
        {
            if (auto data = std::dynamic_pointer_cast<ModelList>(list_item->get_item()))
            {
                label->set_label(ztd::rjust(std::format("{}", data->page), 4));
                image->set_paintable(data->paintable);
            }
        }
    }
}

void
gui::thumbbar::activate(const std::uint32_t position) noexcept
{
    auto item =
        std::dynamic_pointer_cast<Gio::ListModel>(listview_.get_model())->get_object(position);
    if (auto data = std::dynamic_pointer_cast<ModelList>(item))
    {
        signal_page_selected().emit(data->page);
    }
}
