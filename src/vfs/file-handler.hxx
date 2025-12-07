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
#include <memory>
#include <optional>
#include <span>
#include <vector>

#include "settings/settings.hxx"

#include "vfs/extractor.hxx"
#include "vfs/file-provider.hxx"
#include "vfs/image-handler.hxx"

#include "types.hxx"

namespace vfs
{
class file_handler
{
  public:
    file_handler(const std::shared_ptr<config::settings>& settings,
                 const std::shared_ptr<gui::lib::view_state>& view_state);

    void open_file_init(const std::span<const std::filesystem::path> filelist,
                        const page_t start_page = 1) noexcept;

    void open_file(const std::filesystem::path& path, const page_t start_page = 1) noexcept;

    void refresh_opened() noexcept;
    void file_opened() noexcept;
    void file_closed() noexcept;
    void close_file() noexcept;
    [[nodiscard]] bool is_file_loaded() noexcept;
    [[nodiscard]] bool is_archive() noexcept;
    [[nodiscard]] const std::filesystem::path get_base_path() noexcept;
    [[nodiscard]] const std::array<std::int32_t, 2> get_file_number() noexcept;
    [[nodiscard]] const std::filesystem::path get_real_path() noexcept;
    [[nodiscard]] bool open_next_archive() noexcept;
    [[nodiscard]] bool open_prev_archive() noexcept;
    [[nodiscard]] bool open_first_archive() noexcept;
    [[nodiscard]] bool open_last_archive() noexcept;

    [[nodiscard]] std::filesystem::path current_file() noexcept;

    [[nodiscard]] const std::shared_ptr<vfs::image_handler>
    image_handler() const noexcept
    {
        return this->image_handler_;
    }

  private:
    void archive_opened(const std::span<const std::filesystem::path> image_files) noexcept;
    void close(bool close_provider = false) noexcept;
    void initialize_fileprovider(const std::span<const std::filesystem::path> filelist) noexcept;
    void open_archive(const std::filesystem::path& archive) noexcept;
    void file_listed(const std::span<const std::filesystem::path> files) noexcept;
    [[nodiscard]] std::vector<std::filesystem::path>
    sort_archive_images(const std::span<const std::filesystem::path> files) noexcept;
    [[nodiscard]] std::span<const std::filesystem::path> get_file_list() noexcept;

    [[nodiscard]] static std::optional<std::size_t>
    current_file_index(auto&& v, auto& e) noexcept
    {
        const auto it = std::ranges::find(v.cbegin(), v.cend(), e);
        if (it == v.cend())
        {
            return std::nullopt;
        }
        return static_cast<std::size_t>(it - v.cbegin());
    }

    void extracted_file(const std::filesystem::path& filename) noexcept;

  private:
    std::shared_ptr<vfs::image_handler> image_handler_;
    std::unique_ptr<vfs::extractor> extractor_;
    std::unique_ptr<vfs::file_provider> file_provider_;

    std::shared_ptr<config::settings> settings;
    std::shared_ptr<gui::lib::view_state> view_state;

    bool file_loaded_{false};
    bool file_loading_{false};
    bool is_archive_{false};

    std::filesystem::path current_file_path_;
    std::filesystem::path current_file_;
    std::filesystem::path base_path_;

    page_t default_start_page_{1};

  public:
    [[nodiscard]] auto
    signal_file_closed() noexcept
    {
        return this->signal_file_closed_;
    }

    [[nodiscard]] auto
    signal_file_opened() noexcept
    {
        return this->signal_file_opened_;
    }

    [[nodiscard]] auto
    signal_page_set() noexcept
    {
        return this->signal_page_set_;
    }

    [[nodiscard]] auto
    signal_page_available() noexcept
    {
        return this->signal_page_available_;
    }

  private:
    sigc::signal<void()> signal_file_closed_;
    sigc::signal<void()> signal_file_opened_;
    sigc::signal<void(page_t)> signal_page_set_;
    sigc::signal<void(page_t)> signal_page_available_;
};
} // namespace vfs
