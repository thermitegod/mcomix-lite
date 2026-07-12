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
#include <vector>

#include "vfs/utils/natsort/strnatcmp.hxx"
#include "vfs/utils/sort.hxx"

void
vfs::utils::sort_alphanumeric(std::vector<std::filesystem::path>& filelist) noexcept
{
    std::ranges::sort(filelist,
                      [](const std::filesystem::path& a, const std::filesystem::path& b)
                      { return strnatcmp(a.string(), b.string()) < 0; });
}
