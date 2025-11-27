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

namespace gui::lib
{
class view_state
{
  public:
    [[nodiscard]] bool is_manga_mode() const noexcept;
    [[nodiscard]] bool is_displaying_double() const noexcept;

    void set_manga_mode(const bool bval) noexcept;
    void set_displaying_double(const bool bval) noexcept;

  private:
    bool manga_mode_{false};
    bool displaying_double_{false};
};
} // namespace gui::lib
