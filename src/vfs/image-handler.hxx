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

#include <array>
#include <filesystem>
#include <flat_map>
#include <flat_set>
#include <string>
#include <vector>

#include <gdkmm.h>
#include <glibmm.h>

#include "settings/settings.hxx"

#include "gui/lib/view-state.hxx"

#include "vfs/image-files.hxx"

#include "types.hxx"

// #define PIXBUF_BACKEND
// #undef PIXBUF_BACKEND

namespace vfs
{
/**
 * The image_handler keeps track of images, pages, and reads files.
 * When the Filehandler's methods refer to pages, they are indexed from 1,
 * i.e. the first page is page 1 etc.
 * Other modules should *never* read directly from the files pointed to by
 * paths given by the image_handler's methods. The files are not even
 * guaranteed to exist at all times since the extraction of archives is
 * threaded.
 */
class image_handler
{
  public:
    explicit image_handler(const std::shared_ptr<config::settings>& settings,
                           const std::shared_ptr<gui::lib::view_state>& view_state) noexcept;

    [[nodiscard]] std::shared_ptr<vfs::image_files> image_files() const noexcept;

#if defined(PIXBUF_BACKEND)
    [[nodiscard]] std::vector<Glib::RefPtr<Gdk::Pixbuf>>
    get_images(const std::int32_t number) noexcept;
#else
    [[nodiscard]] std::vector<Glib::RefPtr<Gdk::Texture>>
    get_images(const std::int32_t number) noexcept;
#endif

    void set_page(const page_t page) noexcept;

    [[nodiscard]] bool
    is_page_available(const std::optional<page_t> query = std::nullopt) const noexcept;

    void page_available(const page_t page) noexcept;

    void file_available(const std::filesystem::path& filename) noexcept;

    [[nodiscard]] page_t get_number_of_pages() const noexcept;

    [[nodiscard]] page_t get_current_page() const noexcept;

    [[nodiscard]] bool
    is_last_page(const std::optional<page_t> query = std::nullopt) const noexcept;

    [[nodiscard]] std::filesystem::path
    get_path_to_page(const std::optional<page_t> query = std::nullopt) const noexcept;

    [[nodiscard]] const std::vector<std::string>
    get_page_filename(const std::optional<page_t> query = std::nullopt) const noexcept;

    [[nodiscard]] const std::vector<std::string>
    get_page_filesize(const std::optional<page_t> query = std::nullopt) const noexcept;

    [[nodiscard]] std::array<std::int32_t, 2>
    get_page_size(const std::optional<page_t> query = std::nullopt) noexcept;

    [[nodiscard]] std::string
    get_mime_name(const std::optional<page_t> query = std::nullopt) const noexcept;

    [[nodiscard]] Glib::RefPtr<Gdk::Paintable> get_thumbnail(const page_t page,
                                                             const std::int32_t size) noexcept;

    [[nodiscard]] bool is_page_extracted(const std::optional<page_t> query) const noexcept;

  private:
#if defined(PIXBUF_BACKEND)
    [[nodiscard]] Glib::RefPtr<Gdk::Pixbuf> get_image(const page_t page) noexcept;
#else
    [[nodiscard]] Glib::RefPtr<Gdk::Texture> get_image(const page_t page) noexcept;
#endif

    void prune(const std::int32_t start, const std::int32_t size) noexcept;

    std::shared_ptr<vfs::image_files> image_files_;

    std::optional<page_t> current_image_ = std::nullopt;
    std::flat_set<page_t> available_images_;

#if defined(PIXBUF_BACKEND)
    std::flat_map<page_t, Glib::RefPtr<Gdk::Pixbuf>> cache_;
#else
    std::flat_map<page_t, Glib::RefPtr<Gdk::Texture>> cache_;
#endif

    std::shared_ptr<config::settings> settings;
    std::shared_ptr<gui::lib::view_state> view_state;

  public:
    [[nodiscard]] auto
    signal_page_available() noexcept
    {
        return this->signal_page_available_;
    }

  private:
    sigc::signal<void(page_t)> signal_page_available_;
};
} // namespace vfs
