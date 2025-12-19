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

#include <chrono>

#include <gtkmm.h>

#include "vfs/bookmarks.hxx"
#include "vfs/file-handler.hxx"

namespace gui::dialog
{
class bookmarks : public Gtk::ApplicationWindow
{
  public:
    explicit bookmarks(Gtk::ApplicationWindow& parent,
                       const std::shared_ptr<vfs::file_handler>& file_handler,
                       const std::shared_ptr<vfs::bookmarks>& bookmarks,
                       const std::shared_ptr<config::settings>& settings) noexcept;

  private:
    class ModelColumns : public Glib::Object
    {
      public:
        std::filesystem::path path_;
        std::int32_t current_page_;
        std::int32_t total_pages_;
        std::chrono::system_clock::time_point created_;

        static Glib::RefPtr<ModelColumns>
        create(const std::filesystem::path path, const std::int32_t current_page,
               const std::int32_t total_pages,
               const std::chrono::system_clock::time_point created) noexcept
        {
            return Glib::make_refptr_for_instance<ModelColumns>(
                new ModelColumns(path, current_page, total_pages, created));
        }

      protected:
        explicit ModelColumns(const std::filesystem::path path, const std::int32_t current_page,
                              const std::int32_t total_pages,
                              const std::chrono::system_clock::time_point created) noexcept
            : Glib::ObjectBase(typeid(ModelColumns)), path_(path), current_page_(current_page),
              total_pages_(total_pages), created_(created)
        {
        }
    };

    Gtk::Box box_;

    Gtk::ScrolledWindow scrolled_window_;
    Gtk::ColumnView columnview_;
    Glib::RefPtr<Gio::ListStore<ModelColumns>> liststore_;
    Glib::RefPtr<Gtk::SingleSelection> selection_model_;

    Gtk::Box button_box_;
    Gtk::Button button_ok_;
    Gtk::Button button_close_;
    Gtk::Button button_remove_;
    Gtk::Button button_remove_all_;

    std::shared_ptr<vfs::file_handler> file_handler_;
    std::shared_ptr<vfs::bookmarks> bookmarks_;
    std::shared_ptr<config::settings> settings_;

    void create_model() noexcept;
    void add_columns() noexcept;
    void liststore_add_item(const std::filesystem::path path, const std::int32_t current_page,
                            const std::int32_t total_pages,
                            const std::chrono::system_clock::time_point created) noexcept;

    bool on_key_press(std::uint32_t keyval, std::uint32_t keycode,
                      Gdk::ModifierType state) noexcept;
    void on_button_ok_clicked() noexcept;
    void on_button_close_clicked() noexcept;
    void on_button_remove_clicked() noexcept;
    void on_button_remove_all_clicked() noexcept;

    void on_setup_label(const Glib::RefPtr<Gtk::ListItem>& list_item, Gtk::Align halign) noexcept;

    void on_bind_path(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept;
    void on_bind_current_page(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept;
    void on_bind_total_pages(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept;
    void on_bind_created(const Glib::RefPtr<Gtk::ListItem>& list_item) noexcept;
};
} // namespace gui::dialog
