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
                                const std::shared_ptr<gui::lib::view_state>& view_state) noexcept
    : settings(settings), view_state(view_state)
{
}

void
vfs::file_handler::refresh_opened() noexcept
{
    if (!file_loaded_)
    {
        return;
    }

    page_t start_page;
    const auto current_file = get_real_path();

    if (is_archive_)
    {
        start_page = image_handler_->get_current_page();
    }
    else
    {
        start_page = 1;
    }

    open_file(current_file, start_page);
}

void
vfs::file_handler::open_file_init(const std::span<const std::filesystem::path> filelist,
                                  const page_t start_page) noexcept
{
    if (filelist.empty())
    {
        return;
    }

    initialize_fileprovider(filelist);
    open_file(filelist.front(), start_page);
}

void
vfs::file_handler::open_file(const std::filesystem::path& path, const page_t start_page) noexcept
{
    close();

    image_handler_ = std::make_shared<vfs::image_handler>(settings, view_state);
    image_handler_->signal_page_available().connect([this](const page_t page)
                                                    { signal_page_available().emit(page); });

    is_archive_ = vfs::is_archive(path);
    default_start_page_ = start_page;
    current_file_ = path;

    if (is_archive_)
    {
        base_path_ = path;
        file_loading_ = true;
        open_archive(path);
    }
    else
    {
        const auto image_files = file_provider_->list_files(vfs::file_provider::file_type::images);
        if (std::filesystem::is_directory(current_file_))
        {
            base_path_ = current_file_;
        }
        else
        {
            base_path_ = current_file_.parent_path();
        }
        archive_opened(image_files);
    }
}

void
vfs::file_handler::archive_opened(const std::span<const std::filesystem::path> image_files) noexcept
{
    image_handler_->image_files()->set_image_files(image_files);
    file_opened();

    if (image_files.empty())
    {
        logger::error<logger::vfs>("No images in {}", current_file_.string());
        return;
    }

    page_t start_page = default_start_page_;

    if (is_archive_)
    {
        extractor_->extract();
    }
    else
    {
        // No extraction is required, mark all files as available.
        for (const auto& img : image_files)
        {
            image_handler_->file_available(img);
        }

        if (std::filesystem::is_directory(current_file_))
        {
            // if current_file is a directory then start at the first image
            start_page = 1;
        }
        else
        {
            // Set start_page to the same as current_file
            start_page = image_handler_->image_files()->page_from_path(current_file_);
        }
    }

    signal_page_set().emit(start_page);
}

void
vfs::file_handler::file_opened() noexcept
{
    file_loaded_ = true;

    signal_file_opened().emit();
}

void
vfs::file_handler::file_closed() noexcept
{
    signal_file_closed().emit();
}

void
vfs::file_handler::close_file() noexcept
{
    close(true);
}

std::filesystem::path
vfs::file_handler::current_file() noexcept
{
    return current_file_;
}

void
vfs::file_handler::close(bool close_provider) noexcept
{
    if (file_loaded_ || file_loading_)
    {
        if (close_provider)
        {
            file_provider_ = nullptr;
        }
        if (is_archive_)
        {
            extractor_->close();
        }

        image_handler_ = nullptr;

        file_loaded_ = false;
        file_loading_ = false;
        is_archive_ = false;
        current_file_ = "";
        base_path_ = "";

        file_closed();
    }
}

void
vfs::file_handler::initialize_fileprovider(
    const std::span<const std::filesystem::path> filelist) noexcept
{
    file_provider_ = std::make_unique<file_provider>(filelist);
}

void
vfs::file_handler::open_archive(const std::filesystem::path& archive) noexcept
{
    try
    {
        extractor_ = std::make_unique<vfs::extractor>(archive);

        extractor_->signal_file_extracted().connect([this](const std::filesystem::path& file)
                                                    { extracted_file(file); });
        extractor_->signal_file_listed().connect(
            [this](const std::span<const std::filesystem::path> files) { file_listed(files); });

        extractor_->list();
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
    if (!file_loading_)
    {
        return;
    }
    file_loading_ = false;

    archive_opened(sort_archive_images(files));
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
    return file_loaded_;
}

bool
vfs::file_handler::is_archive() noexcept
{
    return is_archive_;
}

const std::filesystem::path
vfs::file_handler::get_base_path() noexcept
{
    return base_path_;
}

std::span<const std::filesystem::path>
vfs::file_handler::get_file_list() noexcept
{
    return file_provider_->list_files(vfs::file_provider::file_type::archives);
}

const std::array<std::int32_t, 2>
vfs::file_handler::get_file_number() noexcept
{
    if (!is_archive_)
    {
        // No file numbers for images.
        return {0, 0};
    }

    const auto files = get_file_list();
    const auto current_index = current_file_index(files, current_file_);

    if (!current_index)
    {
        return {-1, -1};
    }

    return {static_cast<std::int32_t>(*current_index + 1), static_cast<std::int32_t>(files.size())};
}

const std::filesystem::path
vfs::file_handler::get_real_path() noexcept
{
    if (is_archive_)
    {
        return base_path_;
    }
    return image_handler_->get_path_to_page();
}

bool
vfs::file_handler::open_next_archive() noexcept
{
    if (!is_archive())
    {
        return false;
    }

    const auto files = get_file_list();
    const auto current_index = current_file_index(files, current_file_);
    if (!current_index || (*current_index + 1) == files.size())
    {
        return false;
    }

    const auto next_file = files.at(*current_index + 1);

    open_file(next_file, 1);
    return true;
}

bool
vfs::file_handler::open_prev_archive() noexcept
{
    if (!is_archive())
    {
        return false;
    }

    const auto files = get_file_list();
    const auto current_index = current_file_index(files, current_file_);
    if (!current_index || *current_index == 0)
    {
        return false;
    }

    const auto next_file = files.at(*current_index - 1);

    open_file(next_file, 1);
    return true;
}

bool
vfs::file_handler::open_first_archive() noexcept
{
    if (!is_archive())
    {
        return false;
    }

    const auto files = get_file_list();
    const auto next_file = files.front();

    open_file(next_file, 1);
    return true;
}

bool
vfs::file_handler::open_last_archive() noexcept
{
    if (!is_archive())
    {
        return false;
    }

    const auto files = get_file_list();
    const auto next_file = files.back();

    open_file(next_file, 1);
    return true;
}

void
vfs::file_handler::extracted_file(const std::filesystem::path& filename) noexcept
{
    if (!file_loaded_)
    {
        return;
    }

    image_handler_->file_available(filename);
}
