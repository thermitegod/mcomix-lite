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

#include "gui/lib/view-state.hxx"

bool
gui::lib::view_state::is_manga_mode() const noexcept
{
    return this->manga_mode_;
}

bool
gui::lib::view_state::is_displaying_double() const noexcept
{
    return this->displaying_double_;
}

void
gui::lib::view_state::set_manga_mode(const bool bval) noexcept
{
    this->manga_mode_ = bval;
}

void
gui::lib::view_state::set_displaying_double(const bool bval) noexcept
{
    this->displaying_double_ = bval;
}
