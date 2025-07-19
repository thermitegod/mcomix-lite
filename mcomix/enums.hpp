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

enum class Animation
{
    DISABLED = 1,
    NORMAL = 2,
};

enum class ConfigType
{
    CONFIG,
    KEYBINDINGS,
};

enum class DoublePage
{
    NEVER = 0,
    AS_ONE_TITLE = 1,
    AS_ONE_WIDE = 2,
    ALWAYS = 3,
};

enum class FileSortType
{
    NONE = 0,
    NAME = 1,
    SIZE = 2,
    LAST_MODIFIED = 3,
    NAME_LITERAL = 4,
};

enum class FileSortDirection
{
    DESCENDING = 0,
    ASCENDING = 1,
};

enum class FileTypes
{
    IMAGES,
    ARCHIVES,
};

enum class Scroll
{
    END = -4,
    START = -3,
    CENTER = -2,
};

enum class ZoomModes
{
    BEST = 0,
    WIDTH = 1,
    HEIGHT = 2,
    MANUAL = 3,
    SIZE = 4,
};

enum class ZoomAxis
{
    DISTRIBUTION = 0,
    ALIGNMENT = 1,
    WIDTH = 0,
    HEIGHT = 1,
};
