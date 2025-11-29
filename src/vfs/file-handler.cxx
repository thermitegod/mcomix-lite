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
#include <span>
#include <vector>

#include <ztd/ztd.hxx>

#include "settings/settings.hxx"

#include "vfs/extractor.hxx"
#include "vfs/file-handler.hxx"
#include "vfs/file-provider.hxx"
#include "vfs/file-supported.hxx"
#include "vfs/image-handler.hxx"

#include "vfs/utils/sort.hxx"

#include "logger.hxx"

vfs::file_handler::file_handler(const std::shared_ptr<config::settings>& settings,
                                const std::shared_ptr<gui::lib::view_state>& view_state)
    : settings(settings), view_state(view_state)
{
}

void
vfs::file_handler::refresh_opened() noexcept
{
    if (!this->file_loaded_)
    {
        return;
    }

    page_t start_page;
    const auto current_file = this->get_real_path();

    if (this->is_archive_)
    {
        start_page = this->image_handler_->get_current_page();
    }
    else
    {
        start_page = 1;
    }

    this->open_file(current_file, start_page);
}

void
vfs::file_handler::open_file_init(const std::span<const std::filesystem::path> filelist) noexcept
{
    if (filelist.empty())
    {
        return;
    }

    this->initialize_fileprovider(filelist);
    this->open_file(filelist.front(), this->default_start_page_);
}

void
vfs::file_handler::open_file(const std::filesystem::path& path, const page_t start_page) noexcept
{
    this->close();

    this->image_handler_ = std::make_shared<vfs::image_handler>(this->settings, this->view_state);
    this->image_handler_->signal_page_available().connect(
        [this](const page_t page) { this->signal_page_available().emit(page); });

    this->is_archive_ = vfs::is_archive(path);
    this->default_start_page_ = start_page;
    this->current_file_ = path;

    if (this->is_archive_)
    {
        this->base_path_ = path;
        this->file_loading_ = true;
        this->open_archive(path);
    }
    else
    {
        const auto image_files =
            this->file_provider_->list_files(vfs::file_provider::file_type::images);
        if (std::filesystem::is_directory(this->current_file_))
        {
            this->base_path_ = this->current_file_;
        }
        else
        {
            this->base_path_ = this->current_file_.parent_path();
        }
        this->archive_opened(image_files);
    }
}

void
vfs::file_handler::archive_opened(const std::span<const std::filesystem::path> image_files) noexcept
{
    this->image_handler_->image_files()->set_image_files(image_files);
    this->file_opened();

    if (image_files.empty())
    {
        logger::error<logger::vfs>("No images in {}", this->current_file_.string());
        return;
    }

    page_t start_page = this->default_start_page_;

    if (this->is_archive_)
    {
        this->extractor_->extract();
    }
    else
    {
        // No extraction is required, mark all files as available.
        for (const auto& img : image_files)
        {
            this->image_handler_->file_available(img);
        }

        if (std::filesystem::is_directory(this->current_file_))
        {
            // if current_file is a directory then start at the first image
            start_page = 1;
        }
        else
        {
            // Set start_page to the same as current_file
            start_page = this->image_handler_->image_files()->page_from_path(this->current_file_);
        }
    }

    this->signal_page_set().emit(start_page);
}

void
vfs::file_handler::file_opened() noexcept
{
    this->file_loaded_ = true;

    this->signal_file_opened().emit();
}

void
vfs::file_handler::file_closed() noexcept
{
    this->signal_file_closed().emit();
}

void
vfs::file_handler::close_file() noexcept
{
    this->close(true);
}

std::filesystem::path
vfs::file_handler::current_file() noexcept
{
    return this->current_file_;
}

void
vfs::file_handler::close(bool close_provider) noexcept
{
    if (this->file_loaded_ || this->file_loading_)
    {
        if (close_provider)
        {
            this->file_provider_ = nullptr;
        }
        if (this->is_archive_)
        {
            this->extractor_->close();
        }

        this->image_handler_ = nullptr;

        this->file_loaded_ = false;
        this->file_loading_ = false;
        this->is_archive_ = false;
        this->current_file_ = "";
        this->base_path_ = "";

        this->file_closed();
    }
}

void
vfs::file_handler::initialize_fileprovider(
    const std::span<const std::filesystem::path> filelist) noexcept
{
    this->file_provider_ = std::make_unique<file_provider>(filelist);
}

void
vfs::file_handler::open_archive(const std::filesystem::path& archive) noexcept
{
    try
    {
        this->extractor_ = std::make_unique<vfs::extractor>(archive);

        this->extractor_->signal_file_extracted().connect([this](const std::filesystem::path& file)
                                                          { this->extracted_file(file); });
        this->extractor_->signal_file_listed().connect(
            [this](const std::span<const std::filesystem::path> files)
            { this->file_listed(files); });

        this->extractor_->list();
        // this->extractor_->extract();
    }
    catch (const std::exception& ex)
    {
        logger::error<logger::vfs>("failed to open archive: {}", archive.string());
        logger::debug<logger::vfs>("Exception: {}", ex.what());
    }
}

void
vfs::file_handler::file_listed(const std::span<const std::filesystem::path> files) noexcept
{
    if (!this->file_loading_)
    {
        return;
    }
    this->file_loading_ = false;

    this->archive_opened(this->sort_archive_images(files));
}

std::vector<std::filesystem::path>
vfs::file_handler::sort_archive_images(const std::span<const std::filesystem::path> files) noexcept
{
    auto sorted_files = std::vector<std::filesystem::path>{files.cbegin(), files.cend()};
    vfs::utils::sort_alphanumeric(sorted_files);
    return sorted_files;
}

bool
vfs::file_handler::is_file_loaded() noexcept
{
    return this->file_loaded_;
}

bool
vfs::file_handler::is_archive() noexcept
{
    return this->is_archive_;
}

const std::filesystem::path
vfs::file_handler::get_base_path() noexcept
{
    return this->base_path_;
}

std::span<const std::filesystem::path>
vfs::file_handler::get_file_list() noexcept
{
    return this->file_provider_->list_files(vfs::file_provider::file_type::archives);
}

const std::array<std::int32_t, 2>
vfs::file_handler::get_file_number() noexcept
{
    if (!this->is_archive_)
    {
        // No file numbers for images.
        return {0, 0};
    }

    const auto files = this->get_file_list();
    const auto current_index = current_file_index(files, this->current_file_);

    if (!current_index)
    {
        return {-1, -1};
    }

    return {static_cast<std::int32_t>(*current_index + 1), static_cast<std::int32_t>(files.size())};
}

const std::filesystem::path
vfs::file_handler::get_real_path() noexcept
{
    if (this->is_archive_)
    {
        return this->base_path_;
    }
    return this->image_handler_->get_path_to_page();
}

bool
vfs::file_handler::open_next_archive() noexcept
{
    if (!this->is_archive())
    {
        return false;
    }

    const auto files = this->get_file_list();
    if (!std::ranges::contains(files, this->current_file_))
    {
        return false;
    }

    const auto current_index = current_file_index(files, this->current_file_);

    if (!current_index || (*current_index + 1) == files.size())
    {
        return false;
    }

    const auto next_file = files.at(*current_index + 1);
    const page_t next_page = 1;

    this->close();
    this->open_file(next_file, next_page);
    return true;
}

bool
vfs::file_handler::open_prev_archive() noexcept
{
    if (!this->is_archive())
    {
        return false;
    }

    const auto files = this->get_file_list();
    if (!std::ranges::contains(files, this->current_file_))
    {
        return false;
    }

    const auto current_index = current_file_index(files, this->current_file_);

    if (!current_index || *current_index == 0)
    {
        return false;
    }

    const auto next_file = files.at(*current_index - 1);
    const page_t next_page = 1;

    this->close();
    this->open_file(next_file, next_page);
    return true;
}

void
vfs::file_handler::extracted_file(const std::filesystem::path& filename) noexcept
{
    if (!this->file_loaded_)
    {
        return;
    }

    this->image_handler_->file_available(filename);
}
