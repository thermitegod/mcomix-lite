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

    /**
     * Returns number_of_bufs pixbufs for the image(s) that should be
     * currently displayed.
     */
    [[nodiscard]] std::vector<Glib::RefPtr<Gdk::Pixbuf>>
    get_pixbufs(const std::int32_t number) noexcept;

    /**
     * Set up file handler to the page <page>.
     */
    void set_page(const page_t page) noexcept;

    /**
     * Returns true if <page> is available and calls to get_pixbufs
     * would not block. If <page> is std::nullopt, the current page(s) are assumed.
     */
    [[nodiscard]] bool
    is_page_available(const std::optional<page_t> query = std::nullopt) const noexcept;

    /**
     * Called whenever a new page becomes available, i.e. the corresponding file has been extracted.
     */
    void page_available(const page_t page) noexcept;

    /**
     * Called by the file handler when a new file becomes available.
     */
    void file_available(const std::filesystem::path& filename) noexcept;

    /**
     * Return the number of pages in the current archive/directory.
     */
    [[nodiscard]] page_t get_number_of_pages() const noexcept;

    /**
     * Return the current page number (starting from 1), or 0 if no file is loaded.
     */
    [[nodiscard]] page_t get_current_page() const noexcept;

    /**
     * Is <page> the last in a book, if page is std::nullopt use current page.
     */
    [[nodiscard]] bool
    is_last_page(const std::optional<page_t> query = std::nullopt) const noexcept;

    /**
     * Return the full path to the image file for <page>, or the current page if <page> is std::nullopt.
     */
    [[nodiscard]] std::filesystem::path
    get_path_to_page(const std::optional<page_t> query = std::nullopt) const noexcept;

    /**
     * Return a string with the name of the page file.
     */
    [[nodiscard]] const std::vector<std::string>
    get_page_filename(const std::optional<page_t> query = std::nullopt) const noexcept;

    /**
     * Return a list of strings representing the file sizes of the specified pages.
     *
     * @param page: A page number or std::nullopt for the current page.
     * @returns: A list containing the sizes of the specified pages.
     */
    [[nodiscard]] const std::vector<std::string>
    get_page_filesize(const std::optional<page_t> query = std::nullopt) const noexcept;

    /**
     * Return a tuple (width, height) with the size of <page>.
     * If <page> is std::nullopt, return the size of the current page.
     */
    [[nodiscard]] std::array<std::int32_t, 2>
    get_page_size(const std::optional<page_t> query = std::nullopt) noexcept;

    /**
     * Return a string with the name of the mime type of <page>.
     * If <page> is std::nullopt, return the mime type name of the current page.
     */
    [[nodiscard]] std::string
    get_mime_name(const std::optional<page_t> query = std::nullopt) const noexcept;

    /**
     * Return a thumbnail pixbuf of <page> that fits in a box with
     * dimensions <size>x<size>. Return a thumbnail for the current
     * page if <page> is None.
     * If <nowait> is True, don't wait for <page> to be available.
     */
    [[nodiscard]] Glib::RefPtr<Gdk::Paintable> get_thumbnail(const page_t page,
                                                             const std::int32_t size) noexcept;

    /**
     * Checks if the specified page has been extracted.
     */
    [[nodiscard]] bool is_page_extracted(const std::optional<page_t> query) const noexcept;

  private:
    [[nodiscard]] Glib::RefPtr<Gdk::Pixbuf> get_pixbuf(const page_t page) noexcept;

    void prune(const std::int32_t start, const std::int32_t size) noexcept;

    std::shared_ptr<vfs::image_files> image_files_;

    std::optional<page_t> current_image_ = std::nullopt;
    std::flat_set<page_t> available_images_;

    std::flat_map<page_t, Glib::RefPtr<Gdk::Pixbuf>> raw_pixbufs_;
    std::flat_map<page_t, std::array<std::int32_t, 2>> pixbufs_dimensions_;

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
