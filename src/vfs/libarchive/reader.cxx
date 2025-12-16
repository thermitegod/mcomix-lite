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

#include <expected>
#include <filesystem>
#include <fstream>
#include <ios>
#include <memory>

#include <archive_entry.h>

#include "reader.hxx"

namespace vfs::libarchive
{
vfs::libarchive::reader::reader(std::shared_ptr<::archive> ar,
                                std::unique_ptr<reader_context> ctx) noexcept
    : archive_(std::move(ar)), context_(std::move(ctx)),
      current_entry_(std::unexpected(std::make_error_code(std::errc::state_not_recoverable)))
{
}

std::expected<reader, std::error_code>
reader::create(const std::filesystem::path& path) noexcept
{
    constexpr auto BUFFER_SIZE = 16384;

    std::shared_ptr<archive> ar(archive_read_new(), [](archive* a) { archive_read_free(a); });

    auto ctx = std::make_unique<reader_context>(path, BUFFER_SIZE);
    if (!ctx->stream_.is_open())
    {
        return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
    }

    archive_read_support_format_all(ar.get());
    archive_read_support_filter_all(ar.get());

    auto read_callback = [](archive* archive, void* data, const void** buffer) -> ssize_t
    {
        (void)archive;
        auto* ctx = static_cast<reader_context*>(data);

        ctx->stream_.read(ctx->buffer_.data(), static_cast<std::streamsize>(ctx->buffer_.size()));
        *buffer = ctx->buffer_.data();

        return ctx->stream_.gcount();
    };

    const auto result = archive_read_open(ar.get(), ctx.get(), nullptr, read_callback, nullptr);
    if (result != ARCHIVE_OK)
    {
        return std::unexpected(std::make_error_code(std::errc::io_error));
    }

    return reader(std::move(ar), std::move(ctx));
}

void
reader::next_entry() noexcept
{
    if (this->is_finished_)
    {
        return;
    }

    archive_entry* raw_entry = nullptr;
    const auto result = archive_read_next_header(this->archive_.get(), &raw_entry);

    if (result == ARCHIVE_EOF)
    {
        this->is_finished_ = true;
        this->current_entry_ = std::unexpected(std::make_error_code(std::errc::no_message));
    }
    else if (result < ARCHIVE_OK)
    {
        this->is_finished_ = true;
        this->current_entry_ = std::unexpected(std::make_error_code(std::errc::io_error));
    }
    else
    {
        this->current_entry_ = std::make_shared<entry>(raw_entry, this->archive_);
    }
}

reader::iterator
reader::begin() noexcept
{
    this->next_entry();
    return iterator(this);
}

std::default_sentinel_t
reader::end() const noexcept
{
    return {};
}

reader::iterator::reference
reader::iterator::operator*() const noexcept
{
    return this->reader_->current_entry_;
}

reader::iterator&
reader::iterator::operator++() noexcept
{
    this->reader_->next_entry();
    return *this;
}

bool
reader::iterator::operator==(std::default_sentinel_t) const noexcept
{
    return this->reader_->is_finished_;
}
} // namespace vfs::libarchive
