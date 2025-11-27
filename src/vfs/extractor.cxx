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
#include <format>
#include <fstream>
#include <stdexcept>

#include <ztd/ztd.hxx>

#include "vfs/extractor.hxx"
#include "vfs/libarchive/archive_exception.hxx"
#include "vfs/libarchive/archive_reader.hxx"
#include "vfs/user-dirs.hxx"

#include "logger.hxx"

vfs::extractor::extractor(const std::filesystem::path& archive)
    : archive_(archive), destination_(vfs::user::cache() / PACKAGE_NAME / ztd::random_hex())
{
    if (!std::filesystem::exists(this->destination_))
    {
        std::filesystem::create_directories(this->destination_);
    }
}

vfs::extractor::~extractor()
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
vfs::extractor::list()
{
    namespace ar = ns_archive::ns_reader;

    try
    {
        std::fstream fs(this->archive_);
        ns_archive::reader reader =
            ns_archive::reader::make_reader<ar::format::_ALL, ar::filter::_ALL>(fs, 10240);

        std::vector<std::filesystem::path> listed;
        for (auto entry : reader)
        {
            // std::filesystem::path filename = entry->get_header_value_pathname();

            std::filesystem::path filename =
                this->destination_ / entry->get_header_value_pathname();

            if (std::filesystem::is_directory(filename))
            {
                continue;
            }

            // logger::trace<logger::vfs>("archive file: {}", entry->get_header_value_pathname());

            listed.push_back(filename);
        }

        this->signal_file_listed().emit(listed);
    }
    catch (const ns_archive::archive_exception& e)
    {
        logger::error<logger::vfs>("Extraction error: {}", e.what());
        return;
    }
}

void
vfs::extractor::extract()
{
    namespace ar = ns_archive::ns_reader;

    try
    {
        std::fstream fs(this->archive_);
        ns_archive::reader reader =
            ns_archive::reader::make_reader<ar::format::_ALL, ar::filter::_ALL>(fs, 10240);

        for (auto entry : reader)
        {
            std::filesystem::path filename =
                this->destination_ / entry->get_header_value_pathname();

            std::ofstream file(filename);
            if (!file.is_open())
            {
                throw std::runtime_error(
                    std::format("Error opening file for writing: {}", filename.string()));
            }

            // logger::trace<logger::vfs>("Extracting to: {}", filename.string());

            file << entry->get_stream().rdbuf();
            file.close();

            this->signal_file_extracted().emit(filename);
        }
    }
    catch (const ns_archive::archive_exception& e)
    {
        logger::error<logger::vfs>("Extraction error: {}", e.what());
    }
}
