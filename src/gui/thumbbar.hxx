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

#pragma once

#include <filesystem>
#include <thread>

#include <gdkmm.h>
#include <giomm.h>
#include <glibmm.h>
#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include "settings/settings.hxx"

#include "gui/lib/thumbnailer.hxx"

#include "types.hxx"

namespace gui
{
class thumbbar : public Gtk::ScrolledWindow
{
  public:
    explicit thumbbar(const std::shared_ptr<config::settings>& settings) noexcept;
    ~thumbbar() noexcept;

    void request(const page_t page, const std::filesystem::path& filename) noexcept;
    void set_page(const page_t page) noexcept;
    void clear() noexcept;

  protected:
    class ModelList : public Glib::Object
    {
      public:
        page_t page;
        Glib::RefPtr<Gdk::Paintable> paintable;

        static Glib::RefPtr<ModelList>
        create(const page_t page, const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept
        {
            return Glib::make_refptr_for_instance<ModelList>(new ModelList(page, paintable));
        }

      protected:
        explicit ModelList(const page_t page,
                           const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept
            : Glib::ObjectBase(typeid(ModelList)), page(page), paintable(paintable)
        {
        }
    };

    void add_item(const page_t page, const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept;

    void setup_listitem(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept;
    void bind_listitem(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept;
    void activate(const std::uint32_t position) noexcept;

    Gtk::ListView listview_;
    Glib::RefPtr<Gio::ListStore<ModelList>> liststore_;
    Glib::RefPtr<Gtk::SingleSelection> selection_model_;

    Glib::RefPtr<Gtk::ScrollInfo> scroll_info_;

    //
    std::jthread thumbnailer_thread_;
    gui::lib::thumbnailer thumbnailer_;

    std::shared_ptr<config::settings> settings;

  public:
    [[nodiscard]] auto
    signal_page_selected() noexcept
    {
        return this->signal_page_selected_;
    }

  private:
    sigc::signal<void(page_t)> signal_page_selected_;
};
} // namespace gui
