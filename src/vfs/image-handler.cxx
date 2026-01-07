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

#include <algorithm>
#include <filesystem>
#include <memory>
#include <ranges>
#include <string>
#include <vector>

#include <cassert>

#include "settings/settings.hxx"

#include "gui/lib/image-tools.hxx"
#include "gui/lib/view-state.hxx"

#include "vfs/image-files.hxx"
#include "vfs/image-handler.hxx"

#include "vfs/utils/utils.hxx"

#include "logger.hxx"
#include "types.hxx"

vfs::image_handler::image_handler(const std::shared_ptr<config::settings>& settings,
                                  const std::shared_ptr<gui::lib::view_state>& view_state) noexcept
    : settings(settings), view_state(view_state)
{
    this->image_files_ = std::make_shared<vfs::image_files>();
}

std::shared_ptr<vfs::image_files>
vfs::image_handler::image_files() const noexcept
{
    return this->image_files_;
}

void
vfs::image_handler::prune(const std::int32_t start, const std::int32_t size) noexcept
{
    std::erase_if(this->cache_,
                  [start, size](const auto& entry)
                  {
                      const auto key = entry.first;
                      return (key < start || key > (start + size));
                  });
}

#if defined(PIXBUF_BACKEND)
Glib::RefPtr<Gdk::Pixbuf>
#else
Glib::RefPtr<Gdk::Texture>
#endif
vfs::image_handler::get_image(const page_t page) noexcept
{
    if (this->cache_.contains(page))
    {
        // logger::trace<logger::vfs>("page {} in cache", page);
        return this->cache_[page];
    }

    const auto path = this->image_files_->path_from_page(page);

    // logger::trace<logger::vfs>("reading page {} from disk: '{}'", page, path.string());
#if defined(PIXBUF_BACKEND)
    auto image = gui::lib::image_tools::load_pixbuf(path);
#else
    auto image = gui::lib::image_tools::load_texture(path);
#endif
    if (!image)
    {
        return nullptr;
    }

    this->cache_.insert({page, image});
    // logger::trace<logger::vfs>("cache new size {}", this->cache_.size());
    return this->cache_[page];
}

#if defined(PIXBUF_BACKEND)
std::vector<Glib::RefPtr<Gdk::Pixbuf>>
#else
std::vector<Glib::RefPtr<Gdk::Texture>>
#endif
vfs::image_handler::get_images(const std::int32_t number) noexcept
{
    assert(number > 0);

#if defined(PIXBUF_BACKEND)
    std::vector<Glib::RefPtr<Gdk::Pixbuf>> images;
#else
    std::vector<Glib::RefPtr<Gdk::Texture>> images;
#endif
    for (const auto& i : std::views::iota(*this->current_image_) | std::views::take(number))
    {
        images.push_back(vfs::image_handler::get_image(i));
    }

    this->prune(*this->current_image_, static_cast<std::int32_t>(images.size()));

    return images;
}

void
vfs::image_handler::set_page(const page_t page) noexcept
{
    this->current_image_ = page;
}

bool
vfs::image_handler::is_page_available(const std::optional<page_t> query) const noexcept
{
    const auto page = query.value_or(this->get_current_page());

    std::vector<page_t> page_list = {page};
    if (this->view_state->is_displaying_double() && !this->is_last_page(page))
    {
        page_list.push_back(page + 1);
    }

    return std::ranges::all_of(page_list,
                               [this](const page_t page)
                               { return this->available_images_.contains(page); });
}

void
vfs::image_handler::page_available(const page_t page) noexcept
{
    // logger::debug<logger::vfs>("Page is available: {}", page);
    this->available_images_.insert(page);

    this->signal_page_available().emit(page);
}

void
vfs::image_handler::file_available(const std::filesystem::path& filename) noexcept
{
    this->page_available(this->image_files_->page_from_path(filename));
}

page_t
vfs::image_handler::get_number_of_pages() const noexcept
{
    return this->image_files_->total_pages();
}

page_t
vfs::image_handler::get_current_page() const noexcept
{
    return this->current_image_.value_or(0);
}

bool
vfs::image_handler::is_last_page(const std::optional<page_t> query) const noexcept
{
    const auto page = query.value_or(this->get_current_page());

    return page == this->image_files_->total_pages();
}

std::filesystem::path
vfs::image_handler::get_path_to_page(const std::optional<page_t> query) const noexcept
{
    const auto page = query.value_or(this->get_current_page());

    return this->image_files_->path_from_page(page);
}

const std::vector<std::string>
vfs::image_handler::get_page_filename(const std::optional<page_t> query) const noexcept
{
    const auto page = query.value_or(this->get_current_page());

    std::vector<std::string> page_data;

    if (!this->is_page_available(page))
    {
        page_data.push_back("unknown");
        if (this->view_state->is_displaying_double())
        {
            page_data.push_back("unknown");
        }
        return page_data;
    }

    page_data.push_back(this->get_path_to_page(page));

    if (this->view_state->is_displaying_double())
    {
        page_data.push_back(this->get_path_to_page(page + 1));

        if (this->view_state->is_manga_mode())
        {
            std::ranges::reverse(page_data);
        }
    }
    return page_data;
}

const std::vector<std::string>
vfs::image_handler::get_page_filesize(const std::optional<page_t> query) const noexcept
{
    const auto page = query.value_or(this->get_current_page());

    std::vector<std::string> page_data;

    if (!this->is_page_available(page))
    {
        page_data.push_back("unknown");
        if (this->view_state->is_displaying_double())
        {
            page_data.push_back("unknown");
        }
        return page_data;
    }

    page_data.push_back(
        vfs::utils::file_size(this->get_path_to_page(page), this->settings->si_units));

    if (this->view_state->is_displaying_double())
    {
        page_data.push_back(
            vfs::utils::file_size(this->get_path_to_page(page + 1), this->settings->si_units));

        if (this->view_state->is_manga_mode())
        {
            std::ranges::reverse(page_data);
        }
    }
    return page_data;
}

std::array<std::int32_t, 2>
vfs::image_handler::get_page_size(const std::optional<page_t> query) noexcept
{
    const auto page = query.value_or(this->get_current_page());

    std::array<std::int32_t, 2> dimensions = {0, 0};

    if (!this->is_page_available(page))
    {
        return dimensions;
    }

    auto image = this->get_image(page);
    if (!image)
    {
        return dimensions;
    }

    return {image->get_width(), image->get_height()};
}

std::string
vfs::image_handler::get_mime_name(const std::optional<page_t> query) const noexcept
{
    // TODO
    const auto page = query.value_or(this->get_current_page());
    (void)page;
    return "";
}

Glib::RefPtr<Gdk::Paintable>
vfs::image_handler::get_thumbnail(const page_t page, const std::int32_t size) noexcept
{
    if (!this->is_page_extracted(page))
    {
        return nullptr;
    }

    return gui::lib::image_tools::create_thumbnail(this->get_image(page), size);
}

bool
vfs::image_handler::is_page_extracted(const std::optional<page_t> query) const noexcept
{
    const auto page = query.value_or(this->get_current_page());

    return std::ranges::contains(this->available_images_, page);
}
