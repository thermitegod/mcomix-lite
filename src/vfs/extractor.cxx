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

#include <filesystem>

#include <botan/hash.h>
#include <botan/hex.h>

#include <glibmm.h>

#include "vfs/extractor.hxx"
#include "vfs/file-supported.hxx"
#include "vfs/libarchive/reader.hxx"
#include "vfs/user-dirs.hxx"

#include "vfs/utils/utils.hxx"

#include "logger.hxx"

vfs::extractor::extractor(const std::filesystem::path& archive) noexcept : archive_(archive)
{
    const auto hash = std::invoke(
        [](const auto& path)
        {
            const auto uri = Glib::filename_to_uri(path.string());

            const auto md5 = Botan::HashFunction::create("MD5");
            md5->update(uri.data());
            return Botan::hex_encode(md5->final(), false);
        },
        archive);

    this->destination_ = vfs::utils::unique_path(vfs::user::cache() / PACKAGE_NAME, hash, "_");

    if (!std::filesystem::exists(this->destination_))
    {
        std::filesystem::create_directories(this->destination_);
    }
}

vfs::extractor::~extractor() noexcept
{
    this->close();
}

const std::filesystem::path
vfs::extractor::path() const noexcept
{
    return this->destination_;
}

void
vfs::extractor::close() const noexcept
{
    if (std::filesystem::exists(this->destination_))
    {
        std::filesystem::remove_all(this->destination_);
    }
}

void
vfs::extractor::list() noexcept
{
    auto reader = vfs::libarchive::reader::create(this->archive_);
    if (!reader)
    {
        return;
    }

    std::vector<std::filesystem::path> listed;
    for (auto entry_result : *reader)
    {
        if (!entry_result)
        {
            logger::critical<logger::vfs>("Extraction error: {}", entry_result.error().message());
            return;
        }
        auto entry = *entry_result;

        if (!vfs::is_image(entry->get_pathname()))
        {
            continue;
        }

        listed.push_back(this->destination_ / entry->get_pathname());
    }

    this->signal_file_listed().emit(listed);
}

void
vfs::extractor::extract() noexcept
{
    auto reader = vfs::libarchive::reader::create(this->archive_);
    if (!reader)
    {
        return;
    }

    for (auto entry_result : *reader)
    {
        if (!entry_result)
        {
            logger::critical<logger::vfs>("Extraction error: {}", entry_result.error().message());
            return;
        }
        auto entry = *entry_result;

        if (!vfs::is_image(entry->get_pathname()))
        {
            continue;
        }

        const auto path = this->destination_ / entry->get_pathname();

        const auto result = entry->extract(path);
        if (!result)
        {
            logger::critical<logger::vfs>("Extraction error: {}", result.error().message());
            return;
        }

        this->signal_file_extracted().emit(path);
    }
}
